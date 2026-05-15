from app.schemas import AuditResult, ExtractedLine, ExtractedPage
from app.services.analyzer import analyze_page


def test_local_analyzer_returns_valid_audit_without_key(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

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
