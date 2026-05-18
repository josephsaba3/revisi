from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(primary_key=True)
    public_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, default=lambda: uuid4().hex)
    submitted_url: Mapped[str] = mapped_column(Text)
    normalized_url: Mapped[str] = mapped_column(Text)
    brand_voice_source: Mapped[str] = mapped_column(String(64))
    brand_voice_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    page_results: Mapped[list["PageResult"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        order_by="PageResult.id",
    )

    @property
    def page_result(self) -> "PageResult | None":
        return self.page_results[0] if self.page_results else None

    @page_result.setter
    def page_result(self, value: "PageResult") -> None:
        self.page_results = [value]


class PageResult(Base):
    __tablename__ = "page_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    scan_id: Mapped[int] = mapped_column(ForeignKey("scans.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(Text)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    headings: Mapped[list[str]] = mapped_column(JSON, default=list)
    ctas: Mapped[list[str]] = mapped_column(JSON, default=list)
    extracted_copy: Mapped[list[dict]] = mapped_column(JSON, default=list)
    overall_score: Mapped[int] = mapped_column(Integer)
    verdict: Mapped[str] = mapped_column(Text)
    scoring_context: Mapped[str] = mapped_column(Text)
    contextual_modifiers: Mapped[list[str]] = mapped_column(JSON, default=list)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_sludge_risk: Mapped[int] = mapped_column(Integer)
    voice_summary: Mapped[list[str]] = mapped_column(JSON, default=list)
    recommended_next_action: Mapped[str] = mapped_column(Text)
    raw_result: Mapped[dict] = mapped_column(JSON, default=dict)

    scan: Mapped[Scan] = relationship(back_populates="page_results")
    issues: Mapped[list["Issue"]] = relationship(back_populates="page_result", cascade="all, delete-orphan")
    rewrites: Mapped[list["Rewrite"]] = relationship(back_populates="page_result", cascade="all, delete-orphan")


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_result_id: Mapped[int] = mapped_column(ForeignKey("page_results.id", ondelete="CASCADE"), index=True)
    issue_type: Mapped[str] = mapped_column(String(128))
    priority: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(Text)
    line_id: Mapped[str | None] = mapped_column(String(16), nullable=True)
    original_copy: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str] = mapped_column(Text)
    suggested_rewrite: Mapped[str] = mapped_column(Text)

    page_result: Mapped[PageResult] = relationship(back_populates="issues")


class Rewrite(Base):
    __tablename__ = "rewrites"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_result_id: Mapped[int] = mapped_column(ForeignKey("page_results.id", ondelete="CASCADE"), index=True)
    source: Mapped[str] = mapped_column(Text)
    line_id: Mapped[str | None] = mapped_column(String(16), nullable=True)
    original: Mapped[str] = mapped_column(Text)
    rewrite: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(Text)

    page_result: Mapped[PageResult] = relationship(back_populates="rewrites")
