from app.main import _save_scan
from app.schemas import AuditIssue, AuditResult, ExtractedLine, ExtractedPage, RewriteSuggestion, Scorecard
from fastapi.testclient import TestClient
from app.main import app


def test_homepage_renders() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Scan page" in response.text


def test_save_scan_persists_page_result(db_session) -> None:
    page = ExtractedPage(
        url="https://example.com",
        title="Example",
        meta_description="A useful description",
        headings=["Heading"],
        ctas=["Scan page"],
        lines=[ExtractedLine(source="P", text="Useful page copy.")],
    )
    result = AuditResult(
        overall_score=78,
        verdict="Strong, with clear revision targets",
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
                original_copy="Useful page copy.",
                explanation="Needs more detail.",
                suggested_rewrite="Add the concrete task and result.",
            )
        ],
        line_level_rewrites=[
            RewriteSuggestion(
                source="P",
                original="Useful page copy.",
                rewrite="Show the task, reader, and result.",
                reason="More specific.",
            )
        ],
        voice_summary=["Plain and direct"],
        recommended_next_action="Tighten the proof.",
    )

    scan = _save_scan(db_session, "example.com", "https://example.com", None, page, result)

    assert scan.public_token
    assert scan.brand_voice_source == "inferred voice, not confirmed"
    assert scan.page_result.overall_score == 78
    assert scan.page_result.issues[0].issue_type == "Too vague"
