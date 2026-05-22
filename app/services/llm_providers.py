import json
import logging

from anthropic import APIError as AnthropicError
from anthropic import Anthropic
from anthropic import RateLimitError as AnthropicRateLimitError
from openai import OpenAI, OpenAIError, RateLimitError as OpenAIRateLimitError

from app.config import Settings
from app.schemas import AuditResult


logger = logging.getLogger(__name__)


class LLMProviderError(Exception):
    pass


class LLMProviderRateLimitError(LLMProviderError):
    pass


def provider_has_credentials(settings: Settings) -> bool:
    if settings.llm_provider == "anthropic":
        return bool(settings.anthropic_api_key)
    return bool(settings.openai_api_key)


def request_structured_audit(settings: Settings, analysis_prompt: str, payload: dict) -> AuditResult | None:
    if settings.llm_provider == "anthropic":
        return _request_anthropic_audit(settings, analysis_prompt, payload)
    return _request_openai_audit(settings, analysis_prompt, payload)


def _request_openai_audit(settings: Settings, analysis_prompt: str, payload: dict) -> AuditResult | None:
    client = OpenAI(api_key=settings.openai_api_key)

    try:
        response = client.responses.parse(
            model=settings.openai_model,
            reasoning={"effort": settings.openai_reasoning_effort},
            input=[
                {
                    "role": "system",
                    "content": analysis_prompt,
                },
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            text_format=AuditResult,
        )
    except OpenAIRateLimitError as exc:
        raise LLMProviderRateLimitError("OpenAI quota or rate limit hit") from exc
    except OpenAIError as exc:
        raise LLMProviderError("OpenAI audit request failed") from exc

    return response.output_parsed


def _request_anthropic_audit(settings: Settings, analysis_prompt: str, payload: dict) -> AuditResult | None:
    client = Anthropic(api_key=settings.anthropic_api_key)

    try:
        response = client.messages.parse(
            model=settings.anthropic_model,
            max_tokens=settings.anthropic_max_tokens,
            system=analysis_prompt,
            messages=[
                {
                    "role": "user",
                    "content": json.dumps(payload, ensure_ascii=False),
                }
            ],
            output_format=AuditResult,
        )
    except AnthropicRateLimitError as exc:
        raise LLMProviderRateLimitError("Anthropic quota or rate limit hit") from exc
    except AnthropicError as exc:
        raise LLMProviderError("Anthropic audit request failed") from exc

    parsed = response.parsed_output
    if isinstance(parsed, AuditResult):
        return parsed
    if parsed is None:
        return None

    logger.warning("Anthropic returned unexpected parsed audit type: %s", type(parsed).__name__)
    return AuditResult.model_validate(parsed)
