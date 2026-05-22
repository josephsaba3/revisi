import logging

from app.config import get_settings
from app.schemas import AuditIssue, AuditResult, ExtractedPage, RewriteSuggestion, Scorecard

from .llm_providers import (
    LLMProviderError,
    LLMProviderRateLimitError,
    provider_has_credentials,
    request_structured_audit,
)
from .phrase_flags import estimate_ai_sludge_risk, find_phrase_flags
from .scoring import calculate_overall_score, verdict_for_score
from .spec_loader import SCORING_CONTEXT_WEIGHTS, load_rewrite_rules, load_scoring_guide


logger = logging.getLogger(__name__)


def analyze_page(page: ExtractedPage, brand_voice: str | None) -> AuditResult:
    settings = get_settings()
    if not provider_has_credentials(settings):
        return _local_draft_result(page, brand_voice)
    analysis_prompt = (settings.llm_analysis_prompt or settings.openai_analysis_prompt or "").strip()
    if not analysis_prompt:
        raise RuntimeError("LLM_ANALYSIS_PROMPT must be set when an LLM provider API key is configured.")

    payload = _analysis_payload(page, brand_voice)

    try:
        parsed = request_structured_audit(settings, analysis_prompt, payload)
    except LLMProviderRateLimitError:
        provider_name = _provider_name(settings.llm_provider)
        logger.warning("%s quota or rate limit hit; returning local draft result", settings.llm_provider)
        return _local_draft_result(
            page,
            brand_voice,
            note=f"{provider_name} quota or rate limit was hit, so this result uses the local draft checker.",
        )
    except LLMProviderError:
        provider_name = _provider_name(settings.llm_provider)
        logger.exception("%s audit request failed; returning local draft result", settings.llm_provider)
        return _local_draft_result(
            page,
            brand_voice,
            note=f"{provider_name} analysis failed, so this result uses the local draft checker.",
        )
    except Exception:
        logger.exception("Unexpected audit request failure; returning local draft result")
        return _local_draft_result(
            page,
            brand_voice,
            note="Structured analysis failed, so this result uses the local draft checker.",
        )

    if not parsed:
        provider_name = _provider_name(settings.llm_provider)
        logger.error("%s returned no structured audit result; returning local draft result", settings.llm_provider)
        return _local_draft_result(
            page,
            brand_voice,
            note=f"{provider_name} returned no structured result, so this result uses the local draft checker.",
        )

    return _normalize_result(parsed, page)


def _provider_name(raw_provider: str) -> str:
    return {
        "anthropic": "Anthropic",
        "openai": "OpenAI",
    }.get(raw_provider, raw_provider)


def _analysis_payload(page: ExtractedPage, brand_voice: str | None) -> dict:
    text = page.combined_text
    return {
        "task": "Audit this one page for brand voice, clarity, trust, specificity, AI sludge risk, and line-level rewrites.",
        "brand_voice_source": "provided" if brand_voice else "inferred voice, not confirmed",
        "brand_voice": brand_voice or "",
        "page": page.model_dump(exclude={"lines"}),
        "evidence_lines": _evidence_lines(page),
        "deterministic_phrase_hits": [hit.__dict__ for hit in find_phrase_flags(text)],
        "estimated_ai_sludge_risk": estimate_ai_sludge_risk(text),
        "allowed_scoring_contexts": list(SCORING_CONTEXT_WEIGHTS),
        "scoring_guide": load_scoring_guide(),
        "rewrite_rules": load_rewrite_rules(),
        "constraints": [
            "Use exactly one allowed_scoring_contexts value for scoring_context.",
            "Use 2-4 contextual modifiers.",
            "Keep verdict under 80 characters.",
            "Return 3-6 top issues when possible.",
            "Return 3-6 line-level rewrites when possible.",
            "Keep issue_type as a short category label, not a sentence or copy excerpt.",
            "Every top issue and line-level rewrite must include a line_id from evidence_lines.",
            "The original_copy or original field must be copied from the matching evidence line.",
            "Do not invent proof, metrics, customers, awards, guarantees, or product capabilities.",
        ],
    }


def _normalize_result(result: AuditResult, page: ExtractedPage) -> AuditResult:
    scoring_context = _normalize_scoring_context(result.scoring_context)
    overall = calculate_overall_score(result.scores, scoring_context, result.ai_sludge_risk)
    top_issues = _ground_issues(result.top_issues, page)
    rewrites = _ground_rewrites(result.line_level_rewrites, page)
    return result.model_copy(
        update={
            "overall_score": overall,
            "verdict": verdict_for_score(overall),
            "scoring_context": scoring_context,
            "top_issues": top_issues,
            "line_level_rewrites": rewrites,
        }
    )


def _normalize_scoring_context(raw_context: str) -> str:
    context = (raw_context or "").strip()
    if context in SCORING_CONTEXT_WEIGHTS:
        return context

    lowered = context.lower()
    for candidate in SCORING_CONTEXT_WEIGHTS:
        if candidate.lower() in lowered:
            return candidate

    if "saas" in lowered or "software" in lowered or "platform" in lowered or "product-led" in lowered:
        return "SaaS feature page"
    if "dental" in lowered or "healthcare" in lowered or "medical" in lowered:
        return "Dental / healthcare page"
    if "founder" in lowered or "homepage" in lowered:
        return "Founder-led homepage"
    if "blog" in lowered or "educational" in lowered or "article" in lowered:
        return "Blog / educational content"

    logger.warning("Unknown scoring context from analyzer: %s", context[:240])
    return "General brand copy"


def _local_draft_result(page: ExtractedPage, brand_voice: str | None, note: str | None = None) -> AuditResult:
    text = page.combined_text
    hits = find_phrase_flags(text)
    ai_risk = estimate_ai_sludge_risk(text)
    penalty = min(35, len(hits) * 4 + ai_risk // 8)
    has_title = bool(page.title)
    has_meta = bool(page.meta_description)
    has_cta = bool(page.ctas)

    scores = Scorecard(
        brand_fit=70 if brand_voice else 62,
        audience_fit=max(40, 74 - penalty),
        clarity=max(35, 78 - penalty - (0 if has_title else 8)),
        human_sound=max(35, 76 - penalty),
        specificity=max(35, 72 - penalty),
        trust=max(35, 70 - penalty - (0 if has_meta else 6)),
        distinctiveness=max(30, 66 - penalty),
    )
    overall = calculate_overall_score(scores, "General brand copy", ai_risk)

    issues: list[AuditIssue] = []
    for hit in hits[:5]:
        line = _find_line_for_copy(page, hit.phrase)
        issues.append(
            AuditIssue(
                issue_type=hit.category,
                priority="High" if hit.category in {"AI Sludge Phrases", "Could Belong To Any Brand"} else "Medium",
                source=line["source"] if line else "Page copy",
                line_id=line["line_id"] if line else None,
                original_copy=hit.phrase,
                explanation=f"`{hit.phrase}` appears {hit.count} time(s) and may make the page feel less specific.",
                suggested_rewrite="Replace this with a concrete product action, outcome, or proof point from the business.",
            )
        )

    if not has_cta:
        issues.append(
            AuditIssue(
                issue_type="Weak CTA",
                priority="High",
                source="Page",
                line_id=None,
                original_copy="No clear CTA detected",
                explanation="The page needs a visible next step tied to what the reader wants to do.",
                suggested_rewrite="Add a specific action such as `Send your page for review` or `See a sample audit`.",
            )
        )

    rewrites = _draft_rewrites(page, issues)

    voice_summary = [
        "inferred voice, not confirmed" if not brand_voice else "provided brand voice used",
        "Prefer plain, concrete claims over polished category language.",
        "Use specific nouns, proof points, and action-oriented CTAs.",
    ]
    if note:
        voice_summary.insert(0, note)

    return AuditResult(
        overall_score=overall,
        verdict=verdict_for_score(overall),
        scoring_context="General brand copy",
        contextual_modifiers=["Message Hierarchy", "Proof Requirement"],
        scores=scores,
        ai_sludge_risk=ai_risk,
        top_issues=issues[:6],
        line_level_rewrites=rewrites,
        voice_summary=voice_summary,
        recommended_next_action="Add concrete proof and replace generic benefit language before expanding the page scan.",
    )


def _draft_rewrites(page: ExtractedPage, issues: list[AuditIssue]) -> list[RewriteSuggestion]:
    rewrites: list[RewriteSuggestion] = []
    candidate_lines = [line for line in page.lines if 6 <= len(line.text.split()) <= 28]
    for line in candidate_lines[:5]:
        rewrite = line.text
        rewrite = rewrite.replace("streamline", "make")
        rewrite = rewrite.replace("unlock", "show")
        rewrite = rewrite.replace("powerful", "focused")
        if rewrite == line.text:
            rewrite = f"{line.text} [make this more specific with a concrete proof point]"
        rewrites.append(
            RewriteSuggestion(
                source=line.source,
                line_id=_line_id(line, len(rewrites)),
                original=line.text,
                rewrite=rewrite,
                reason="Draft local rewrite. Add brand-specific detail before publishing.",
            )
        )
    return rewrites


def _evidence_lines(page: ExtractedPage) -> list[dict[str, str]]:
    lines: list[dict[str, str]] = []
    for index, line in enumerate(page.lines):
        text = line.text.strip()
        if not text:
            continue
        lines.append(
            {
                "line_id": _line_id(line, index),
                "source": line.source,
                "text": text[:1200],
            }
        )
    return lines


def _line_id(line, index: int) -> str:
    return line.line_id or f"L{index + 1:03d}"


def _ground_issues(issues: list[AuditIssue], page: ExtractedPage) -> list[AuditIssue]:
    grounded: list[AuditIssue] = []
    for issue in issues:
        line = _matching_line(page, issue.line_id, issue.original_copy)
        if not line:
            logger.warning("Dropping ungrounded audit issue: %s", issue.original_copy[:120])
            continue
        grounded.append(
            issue.model_copy(
                update={
                    "line_id": line["line_id"],
                    "source": line["source"],
                    "original_copy": _grounded_excerpt(issue.original_copy, line["text"]),
                }
            )
        )
    return grounded


def _ground_rewrites(rewrites: list[RewriteSuggestion], page: ExtractedPage) -> list[RewriteSuggestion]:
    grounded: list[RewriteSuggestion] = []
    for rewrite in rewrites:
        line = _matching_line(page, rewrite.line_id, rewrite.original)
        if not line:
            logger.warning("Dropping ungrounded rewrite suggestion: %s", rewrite.original[:120])
            continue
        grounded.append(
            rewrite.model_copy(
                update={
                    "line_id": line["line_id"],
                    "source": line["source"],
                    "original": _grounded_excerpt(rewrite.original, line["text"]),
                }
            )
        )
    return grounded


def _matching_line(page: ExtractedPage, line_id: str | None, quoted_copy: str) -> dict[str, str] | None:
    evidence = _evidence_lines(page)
    if line_id:
        for line in evidence:
            if line["line_id"] == line_id and _contains_copy(line["text"], quoted_copy):
                return line
    return _find_line_for_copy(page, quoted_copy)


def _find_line_for_copy(page: ExtractedPage, quoted_copy: str) -> dict[str, str] | None:
    for line in _evidence_lines(page):
        if _contains_copy(line["text"], quoted_copy):
            return line
    return None


def _contains_copy(line_text: str, quoted_copy: str) -> bool:
    quoted = _normalized_space(quoted_copy)
    if not quoted:
        return False
    return quoted.lower() in _normalized_space(line_text).lower()


def _grounded_excerpt(quoted_copy: str, line_text: str) -> str:
    quoted = quoted_copy.strip()
    return quoted if quoted else line_text


def _normalized_space(value: str) -> str:
    return " ".join((value or "").split())
