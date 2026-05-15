import json

from openai import OpenAI
from pydantic import ValidationError

from app.config import get_settings
from app.schemas import AuditIssue, AuditResult, ExtractedPage, RewriteSuggestion, Scorecard

from .phrase_flags import estimate_ai_sludge_risk, find_phrase_flags
from .scoring import calculate_overall_score, verdict_for_score
from .spec_loader import load_rewrite_rules, load_scoring_guide


def analyze_page(page: ExtractedPage, brand_voice: str | None) -> AuditResult:
    settings = get_settings()
    if not settings.openai_api_key:
        return _local_draft_result(page, brand_voice)

    client = OpenAI(api_key=settings.openai_api_key)
    payload = _analysis_payload(page, brand_voice)

    response = client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a brand voice and clarity auditor. Return only structured data. "
                    "Preserve source claims, never invent proof, and label inferred voice carefully."
                ),
            },
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        text_format=AuditResult,
    )

    parsed = response.output_parsed
    if not parsed:
        raise RuntimeError("OpenAI returned no structured audit result.")

    return _normalize_result(parsed)


def _analysis_payload(page: ExtractedPage, brand_voice: str | None) -> dict:
    text = page.combined_text
    return {
        "task": "Audit this one page for brand voice, clarity, trust, specificity, AI sludge risk, and line-level rewrites.",
        "brand_voice_source": "provided" if brand_voice else "inferred voice, not confirmed",
        "brand_voice": brand_voice or "",
        "page": page.model_dump(),
        "deterministic_phrase_hits": [hit.__dict__ for hit in find_phrase_flags(text)],
        "estimated_ai_sludge_risk": estimate_ai_sludge_risk(text),
        "scoring_guide": load_scoring_guide(),
        "rewrite_rules": load_rewrite_rules(),
        "constraints": [
            "Use one of the existing scoring contexts.",
            "Use 2-4 contextual modifiers.",
            "Return 3-6 top issues when possible.",
            "Return 3-6 line-level rewrites when possible.",
            "Do not invent proof, metrics, customers, awards, guarantees, or product capabilities.",
        ],
    }


def _normalize_result(result: AuditResult) -> AuditResult:
    overall = calculate_overall_score(result.scores, result.scoring_context, result.ai_sludge_risk)
    return result.model_copy(update={"overall_score": overall, "verdict": verdict_for_score(overall)})


def _local_draft_result(page: ExtractedPage, brand_voice: str | None) -> AuditResult:
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
        issues.append(
            AuditIssue(
                issue_type=hit.category,
                priority="High" if hit.category in {"AI Sludge Phrases", "Could Belong To Any Brand"} else "Medium",
                source="Page copy",
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
                original_copy="No clear CTA detected",
                explanation="The page needs a visible next step tied to what the reader wants to do.",
                suggested_rewrite="Add a specific action such as `Send your page for review` or `See a sample audit`.",
            )
        )

    rewrites = _draft_rewrites(page, issues)

    return AuditResult(
        overall_score=overall,
        verdict=verdict_for_score(overall),
        scoring_context="General brand copy",
        contextual_modifiers=["Message Hierarchy", "Proof Requirement"],
        scores=scores,
        ai_sludge_risk=ai_risk,
        top_issues=issues[:6],
        line_level_rewrites=rewrites,
        voice_summary=[
            "inferred voice, not confirmed" if not brand_voice else "provided brand voice used",
            "Prefer plain, concrete claims over polished category language.",
            "Use specific nouns, proof points, and action-oriented CTAs.",
        ],
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
                original=line.text,
                rewrite=rewrite,
                reason="Draft local rewrite. Add brand-specific detail before publishing.",
            )
        )
    return rewrites
