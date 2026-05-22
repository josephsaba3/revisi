from app.config import Settings
from app.schemas import AuditResult, Scorecard
from app.services import llm_providers


def _audit_result() -> AuditResult:
    return AuditResult(
        overall_score=80,
        verdict="Strong, with clear revision targets",
        scoring_context="General brand copy",
        contextual_modifiers=["Message Hierarchy"],
        scores=Scorecard(
            brand_fit=80,
            audience_fit=80,
            clarity=80,
            human_sound=80,
            specificity=80,
            trust=80,
            distinctiveness=80,
        ),
        ai_sludge_risk=20,
        top_issues=[],
        line_level_rewrites=[],
        voice_summary=["Clear and specific."],
        recommended_next_action="Tighten the CTA.",
    )


def test_openai_provider_preserves_structured_response_call(monkeypatch) -> None:
    call_kwargs = {}
    parsed_result = _audit_result()

    class FakeResponse:
        output_parsed = parsed_result

    class FakeResponses:
        def parse(self, **kwargs):
            call_kwargs.update(kwargs)
            return FakeResponse()

    class FakeOpenAI:
        def __init__(self, **kwargs):
            call_kwargs["client"] = kwargs
            self.responses = FakeResponses()

    monkeypatch.setattr(llm_providers, "OpenAI", FakeOpenAI)

    result = llm_providers.request_structured_audit(
        Settings(
            llm_provider="openai",
            openai_api_key="openai-test",
            openai_model="gpt-5.5",
            openai_reasoning_effort="low",
        ),
        "Private prompt",
        {"page": {"url": "https://example.com"}},
    )

    assert result == parsed_result
    assert call_kwargs["client"]["api_key"] == "openai-test"
    assert call_kwargs["model"] == "gpt-5.5"
    assert call_kwargs["reasoning"] == {"effort": "low"}
    assert call_kwargs["input"][0]["content"] == "Private prompt"


def test_anthropic_provider_uses_messages_parse(monkeypatch) -> None:
    call_kwargs = {}
    parsed_result = _audit_result()

    class FakeResponse:
        parsed_output = parsed_result

    class FakeMessages:
        def parse(self, **kwargs):
            call_kwargs.update(kwargs)
            return FakeResponse()

    class FakeAnthropic:
        def __init__(self, **kwargs):
            call_kwargs["client"] = kwargs
            self.messages = FakeMessages()

    monkeypatch.setattr(llm_providers, "Anthropic", FakeAnthropic)

    result = llm_providers.request_structured_audit(
        Settings(
            llm_provider="anthropic",
            anthropic_api_key="anthropic-test",
            anthropic_model="claude-sonnet-4-6",
            anthropic_max_tokens=12000,
            anthropic_effort="medium",
        ),
        "Private prompt",
        {"page": {"url": "https://example.com"}},
    )

    assert result == parsed_result
    assert call_kwargs["client"]["api_key"] == "anthropic-test"
    assert call_kwargs["model"] == "claude-sonnet-4-6"
    assert call_kwargs["max_tokens"] == 12000
    assert call_kwargs["system"] == "Private prompt"
    assert call_kwargs["output_format"] is AuditResult
    assert call_kwargs["output_config"] == {"effort": "medium"}
    assert call_kwargs["extra_body"] == {"cache_control": {"type": "ephemeral"}}


def test_anthropic_provider_can_disable_prompt_cache(monkeypatch) -> None:
    call_kwargs = {}
    parsed_result = _audit_result()

    class FakeResponse:
        parsed_output = parsed_result

    class FakeMessages:
        def parse(self, **kwargs):
            call_kwargs.update(kwargs)
            return FakeResponse()

    class FakeAnthropic:
        def __init__(self, **_kwargs):
            self.messages = FakeMessages()

    monkeypatch.setattr(llm_providers, "Anthropic", FakeAnthropic)

    result = llm_providers.request_structured_audit(
        Settings(
            llm_provider="anthropic",
            anthropic_api_key="anthropic-test",
            anthropic_effort="low",
            anthropic_prompt_cache_enabled=False,
        ),
        "Private prompt",
        {"page": {"url": "https://example.com"}},
    )

    assert result == parsed_result
    assert call_kwargs["output_config"] == {"effort": "low"}
    assert "extra_body" not in call_kwargs
