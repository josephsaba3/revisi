from app.config import get_settings
from app.main import _save_scan, _scan_attempts
from app.schemas import AuditIssue, AuditResult, ExtractedLine, ExtractedPage, RewriteSuggestion, Scorecard
from fastapi.testclient import TestClient
from app.main import app, get_db


def test_homepage_renders() -> None:
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Run the audit" in response.text


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
                line_id="L001",
                original_copy="Useful page copy.",
                explanation="Needs more detail.",
                suggested_rewrite="Add the concrete task and result.",
            )
        ],
        line_level_rewrites=[
            RewriteSuggestion(
                source="P",
                line_id="L001",
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
    assert scan.page_result.issues[0].line_id == "L001"
    assert scan.page_result.rewrites[0].line_id == "L001"


def test_save_scan_accepts_long_report_text(db_session) -> None:
    page = ExtractedPage(
        url="https://stripe.com",
        title="Stripe",
        meta_description="Payments infrastructure",
        headings=["Financial infrastructure"],
        ctas=["Start now"],
        lines=[ExtractedLine(source="H1", text="Financial infrastructure to grow your revenue")],
    )
    long_context = "SaaS feature page. " + ("Complex financial infrastructure homepage. " * 12)
    long_context = long_context.strip()
    result = AuditResult(
        overall_score=78,
        verdict="Strong, with clear revision targets",
        scoring_context=long_context,
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
        top_issues=[],
        line_level_rewrites=[],
        voice_summary=["Plain and direct"],
        recommended_next_action="Tighten the hero and product-section intro first.",
    )

    scan = _save_scan(db_session, "stripe.com", "https://stripe.com", None, page, result)

    assert scan.page_result.scoring_context == long_context


def test_result_page_renders(db_session) -> None:
    page = ExtractedPage(
        url="https://example.com",
        title="Example",
        meta_description="A useful description",
        headings=["Heading"],
        ctas=["Run the audit"],
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
        top_issues=[],
        line_level_rewrites=[],
        voice_summary=[
            "OpenAI quota or rate limit was hit, so this result uses the local draft checker.",
            "Plain and direct",
        ],
        recommended_next_action="Tighten the proof.",
    )
    scan = _save_scan(db_session, "example.com", "https://example.com", None, page, result)
    app.dependency_overrides[get_db] = lambda: db_session
    client = TestClient(app)

    try:
        response = client.get(f"/r/{scan.public_token}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Revisi Brand Audit Report" in response.text
    assert "Lower-confidence result" in response.text
    assert "Plain and direct" in response.text


def test_scan_rate_limit_blocks_repeated_posts(monkeypatch) -> None:
    monkeypatch.setenv("SCAN_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("SCAN_RATE_LIMIT_COUNT", "5")
    monkeypatch.setenv("SCAN_RATE_LIMIT_WINDOW_SECONDS", "600")
    get_settings.cache_clear()
    _scan_attempts.clear()
    client = TestClient(app)
    headers = {"CF-Connecting-IP": "203.0.113.10"}

    try:
        for _ in range(5):
            response = client.post("/scan", data={"url": "ftp://example.com", "brand_voice": ""}, headers=headers)
            assert response.status_code == 400

        limited = client.post("/scan", data={"url": "ftp://example.com", "brand_voice": ""}, headers=headers)

        assert limited.status_code == 429
        assert "Too many scans from this connection. Try again soon." in limited.text
    finally:
        _scan_attempts.clear()
        monkeypatch.delenv("SCAN_RATE_LIMIT_ENABLED", raising=False)
        monkeypatch.delenv("SCAN_RATE_LIMIT_COUNT", raising=False)
        monkeypatch.delenv("SCAN_RATE_LIMIT_WINDOW_SECONDS", raising=False)
        get_settings.cache_clear()
