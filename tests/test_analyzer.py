from app.config import get_settings
from app.schemas import AuditIssue, AuditResult, ExtractedLine, ExtractedPage, RewriteSuggestion, Scorecard
from app.services import analyzer
from app.services.analyzer import analyze_page
from app.services.llm_providers import LLMProviderRateLimitError


def test_audit_issue_trims_long_model_issue_type() -> None:
    issue = AuditIssue(
        issue_type="Vague promise - keep every test organized without the operational proof needed by busy decision makers",
        priority="High",
        source="P",
        line_id="L001",
        original_copy="Keep every test organized.",
        explanation="Needs a shorter category label.",
        suggested_rewrite="Name the concrete task.",
    )

    assert len(issue.issue_type) == 80
    assert issue.issue_type.startswith("Vague promise")


def test_local_analyzer_returns_valid_audit_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    get_settings.cache_clear()

    page = ExtractedPage(
        url="https://example.com",
        title="Example",
        meta_description=None,
        headings=["Example"],
        ctas=[],
        lines=[
            ExtractedLine(source="H1", text="Unlock the power of effortless growth"),
            ExtractedLine(source="P", text="Our all-in-one solution helps modern teams streamline operations."),
        ],
    )

    result = analyze_page(page, None)

    assert isinstance(result, AuditResult)
    assert result.overall_score <= 100
    assert result.voice_summary[0] == "inferred voice, not confirmed"
    assert result.top_issues


def test_analyzer_labels_openai_quota_fallback(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_ANALYSIS_PROMPT", "Private audit prompt")
    get_settings.cache_clear()

    def fake_request(*_args, **_kwargs):
        raise LLMProviderRateLimitError("quota exceeded")

    monkeypatch.setattr(analyzer, "request_structured_audit", fake_request)
    page = ExtractedPage(
        url="https://example.com",
        title="Example",
        meta_description=None,
        headings=["Example"],
        ctas=[],
        lines=[
            ExtractedLine(source="H1", text="Unlock seamless growth for modern teams"),
            ExtractedLine(source="P", text="Our all-in-one solution helps modern teams streamline operations."),
        ],
    )

    result = analyze_page(page, None)

    assert isinstance(result, AuditResult)
    assert result.voice_summary[0] == "OpenAI quota or rate limit was hit, so this result uses the local draft checker."
    assert result.top_issues
    assert result.overall_score <= 100

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_ANALYSIS_PROMPT", raising=False)
    get_settings.cache_clear()


def test_analyzer_normalizes_explanatory_scoring_context(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM_ANALYSIS_PROMPT", "Private audit prompt")
    get_settings.cache_clear()

    parsed_result = AuditResult(
        overall_score=78,
        verdict="Strong, with clear revision targets",
        scoring_context=(
            "SaaS feature page. Although this is a homepage, it functions as a "
            "product-led platform page for a complex payments offer."
        ),
        contextual_modifiers=["Message Hierarchy"],
        scores=Scorecard(
            brand_fit=88,
            audience_fit=80,
            clarity=82,
            human_sound=77,
            specificity=78,
            trust=83,
            distinctiveness=72,
        ),
        ai_sludge_risk=28,
        top_issues=[],
        line_level_rewrites=[],
        voice_summary=["Inferred voice only, not confirmed."],
        recommended_next_action="Tighten the hero and product-section intro first.",
    )

    monkeypatch.setattr(analyzer, "request_structured_audit", lambda *_args, **_kwargs: parsed_result)
    page = ExtractedPage(
        url="https://stripe.com",
        title="Stripe",
        meta_description="Payments infrastructure",
        headings=["Financial infrastructure"],
        ctas=["Start now"],
        lines=[ExtractedLine(source="H1", text="Financial infrastructure to grow your revenue")],
    )

    result = analyze_page(page, None)

    assert result.scoring_context == "SaaS feature page"
    assert result.verdict
    assert result.overall_score <= 100

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("LLM_ANALYSIS_PROMPT", raising=False)
    get_settings.cache_clear()


def test_analyzer_uses_low_reasoning_and_drops_ungrounded_output(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-5.5")
    monkeypatch.setenv("OPENAI_REASONING_EFFORT", "low")
    monkeypatch.setenv("LLM_ANALYSIS_PROMPT", "Use the private prompt from env.")
    get_settings.cache_clear()
    call_kwargs = {}

    parsed_result = AuditResult(
        overall_score=99,
        verdict="Invented verdict",
        scoring_context="General brand copy",
        contextual_modifiers=["Message Hierarchy"],
        scores=Scorecard(
            brand_fit=80,
            audience_fit=80,
            clarity=80,
            human_sound=80,
            specificity=70,
            trust=75,
            distinctiveness=70,
        ),
        ai_sludge_risk=20,
        top_issues=[
            AuditIssue(
                issue_type="Too vague",
                priority="High",
                source="P",
                line_id="L001",
                original_copy="Useful page copy.",
                explanation="Needs more detail.",
                suggested_rewrite="Add the concrete task and result.",
            ),
            AuditIssue(
                issue_type="Invented proof",
                priority="High",
                source="P",
                line_id="L002",
                original_copy="Trusted by 10,000 teams.",
                explanation="This was not on the page.",
                suggested_rewrite="Remove it.",
            ),
        ],
        line_level_rewrites=[
            RewriteSuggestion(
                source="P",
                line_id=None,
                original="Useful page copy.",
                rewrite="Show the task, reader, and result.",
                reason="More specific.",
            ),
            RewriteSuggestion(
                source="P",
                line_id="L002",
                original="Made-up source copy.",
                rewrite="Still made up.",
                reason="Not grounded.",
            ),
        ],
        voice_summary=["Inferred voice only, not confirmed."],
        recommended_next_action="Tighten the proof.",
    )

    def fake_request(settings, prompt, payload):
        call_kwargs.update(
            {
                "settings": settings,
                "prompt": prompt,
                "payload": payload,
            }
        )
        return parsed_result

    monkeypatch.setattr(analyzer, "request_structured_audit", fake_request)
    page = ExtractedPage(
        url="https://example.com",
        title="Example",
        meta_description="A useful description",
        headings=["Heading"],
        ctas=["Run the audit"],
        lines=[ExtractedLine(line_id="L001", source="P", text="Useful page copy.")],
    )

    result = analyze_page(page, None)

    assert call_kwargs["settings"].openai_reasoning_effort == "low"
    assert call_kwargs["settings"].openai_model == "gpt-5.5"
    assert call_kwargs["prompt"] == "Use the private prompt from env."
    assert call_kwargs["payload"]["page"]["url"] == "https://example.com"
    assert result.verdict == "Strong, with clear revision targets"
    assert [issue.original_copy for issue in result.top_issues] == ["Useful page copy."]
    assert result.top_issues[0].line_id == "L001"
    assert [rewrite.original for rewrite in result.line_level_rewrites] == ["Useful page copy."]
    assert result.line_level_rewrites[0].line_id == "L001"

    monkeypatch.delenv("LLM_PROVIDER", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
    monkeypatch.delenv("LLM_ANALYSIS_PROMPT", raising=False)
    get_settings.cache_clear()


def test_llm_prompt_is_required_with_api_key(monkeypatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.delenv("LLM_ANALYSIS_PROMPT", raising=False)
    monkeypatch.delenv("OPENAI_ANALYSIS_PROMPT", raising=False)
    get_settings.cache_clear()

    page = ExtractedPage(
        url="https://example.com",
        title="Example",
        meta_description="A useful description",
        headings=["Heading"],
        ctas=["Run the audit"],
        lines=[ExtractedLine(line_id="L001", source="P", text="Useful page copy.")],
    )

    try:
        analyze_page(page, None)
    except RuntimeError as exc:
        assert "LLM_ANALYSIS_PROMPT" in str(exc)
    else:
        raise AssertionError("Expected LLM_ANALYSIS_PROMPT to be required")
    finally:
        monkeypatch.delenv("LLM_PROVIDER", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        get_settings.cache_clear()
