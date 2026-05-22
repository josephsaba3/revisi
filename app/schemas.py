from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


CORE_SCORE_KEYS = (
    "brand_fit",
    "audience_fit",
    "clarity",
    "human_sound",
    "specificity",
    "trust",
    "distinctiveness",
)

Priority = Literal["High", "Medium", "Low"]


def _trim_string(value: object, max_length: int) -> object:
    if isinstance(value, str):
        return value.strip()[:max_length]
    return value


class ScanRequest(BaseModel):
    url: HttpUrl
    brand_voice: str | None = None


class ExtractedLine(BaseModel):
    line_id: str = ""
    source: str
    text: str


class ExtractedPage(BaseModel):
    url: str
    title: str | None = None
    meta_description: str | None = None
    headings: list[str] = Field(default_factory=list)
    ctas: list[str] = Field(default_factory=list)
    lines: list[ExtractedLine] = Field(default_factory=list)

    @property
    def combined_text(self) -> str:
        return "\n".join(line.text for line in self.lines)


class Scorecard(BaseModel):
    brand_fit: int = Field(ge=0, le=100)
    audience_fit: int = Field(ge=0, le=100)
    clarity: int = Field(ge=0, le=100)
    human_sound: int = Field(ge=0, le=100)
    specificity: int = Field(ge=0, le=100)
    trust: int = Field(ge=0, le=100)
    distinctiveness: int = Field(ge=0, le=100)


class AuditIssue(BaseModel):
    issue_type: str = Field(max_length=80)
    priority: Priority
    source: str = Field(max_length=80)
    line_id: str | None = Field(default=None, max_length=16)
    original_copy: str = Field(max_length=600)
    explanation: str = Field(max_length=800)
    suggested_rewrite: str = Field(max_length=800)

    @field_validator("issue_type", mode="before")
    @classmethod
    def keep_issue_type_short(cls, value: object) -> object:
        return _trim_string(value, 80)

    @field_validator("source", mode="before")
    @classmethod
    def keep_source_short(cls, value: object) -> object:
        return _trim_string(value, 80)

    @field_validator("original_copy", mode="before")
    @classmethod
    def keep_original_copy_bounded(cls, value: object) -> object:
        return _trim_string(value, 600)

    @field_validator("explanation", "suggested_rewrite", mode="before")
    @classmethod
    def keep_issue_notes_bounded(cls, value: object) -> object:
        return _trim_string(value, 800)


class RewriteSuggestion(BaseModel):
    source: str = Field(max_length=80)
    line_id: str | None = Field(default=None, max_length=16)
    original: str = Field(max_length=600)
    rewrite: str = Field(max_length=800)
    reason: str = Field(max_length=500)

    @field_validator("source", mode="before")
    @classmethod
    def keep_source_short(cls, value: object) -> object:
        return _trim_string(value, 80)

    @field_validator("original", mode="before")
    @classmethod
    def keep_original_bounded(cls, value: object) -> object:
        return _trim_string(value, 600)

    @field_validator("rewrite", mode="before")
    @classmethod
    def keep_rewrite_bounded(cls, value: object) -> object:
        return _trim_string(value, 800)

    @field_validator("reason", mode="before")
    @classmethod
    def keep_reason_bounded(cls, value: object) -> object:
        return _trim_string(value, 500)


class AuditResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    verdict: str = Field(max_length=80)
    scoring_context: str
    contextual_modifiers: list[str] = Field(default_factory=list, max_length=4)
    scores: Scorecard
    ai_sludge_risk: int = Field(ge=0, le=100)
    top_issues: list[AuditIssue] = Field(default_factory=list, max_length=8)
    line_level_rewrites: list[RewriteSuggestion] = Field(default_factory=list, max_length=8)
    voice_summary: list[str] = Field(default_factory=list, max_length=6)
    recommended_next_action: str = Field(max_length=900)

    @field_validator("verdict", mode="before")
    @classmethod
    def keep_verdict_short(cls, value: object) -> object:
        return _trim_string(value, 80)

    @field_validator("recommended_next_action", mode="before")
    @classmethod
    def keep_next_action_bounded(cls, value: object) -> object:
        return _trim_string(value, 900)

    @field_validator("verdict", "scoring_context", "recommended_next_action")
    @classmethod
    def not_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value
