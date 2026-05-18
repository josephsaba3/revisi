from app.config import get_settings
from app import main
from app.main import _complete_job, _create_scan_job, _perform_scan, _save_scan, _scan_attempts, _scan_jobs
from app.schemas import AuditIssue, AuditResult, ExtractedLine, ExtractedPage, RewriteSuggestion, Scorecard
from app.services.extractor import FetchError
from fastapi.testclient import TestClient
from app.main import app, get_db
from urllib import robotparser


def _allow_all_robots():
    parser = robotparser.RobotFileParser()
    parser.parse([])
    return parser


def _disallow_all_robots():
    parser = robotparser.RobotFileParser()
    parser.parse(["User-agent: *", "Disallow: /"])
    return parser


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
        top_issues=[
            AuditIssue(
                issue_type="Too vague",
                priority="Medium",
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
                line_id="L031",
                original="Useful page copy.",
                rewrite="Show the task, reader, and result.",
                reason="More specific.",
            )
        ],
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
    assert "Export PDF" in response.text
    assert "Share" in response.text
    assert "Lower-confidence result" in response.text
    assert "Plain and direct" in response.text
    assert "Keep this direction visible when revising the page." not in response.text
    assert "L001" not in response.text
    assert "L031" not in response.text


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
            assert response.status_code == 202

        limited = client.post("/scan", data={"url": "ftp://example.com", "brand_voice": ""}, headers=headers)

        assert limited.status_code == 429
        assert limited.json()["error"] == "Too many scans from this connection. Try again soon."
    finally:
        _scan_attempts.clear()
        _scan_jobs.clear()
        monkeypatch.delenv("SCAN_RATE_LIMIT_ENABLED", raising=False)
        monkeypatch.delenv("SCAN_RATE_LIMIT_COUNT", raising=False)
        monkeypatch.delenv("SCAN_RATE_LIMIT_WINDOW_SECONDS", raising=False)
        get_settings.cache_clear()


def test_scan_post_returns_job_id(monkeypatch) -> None:
    async def fake_run_scan_job(*_args, **_kwargs):
        return None

    monkeypatch.setattr(main, "_run_scan_job", fake_run_scan_job)
    _scan_attempts.clear()
    _scan_jobs.clear()
    client = TestClient(app)

    try:
        response = client.post("/scan", data={"url": "example.com", "brand_voice": ""})

        assert response.status_code == 202
        assert response.json()["job_id"] in _scan_jobs
    finally:
        _scan_attempts.clear()
        _scan_jobs.clear()


def test_scan_progress_returns_done_report_url() -> None:
    _scan_jobs.clear()
    job_id = _create_scan_job()
    _complete_job(job_id, "/r/test-token")
    client = TestClient(app)

    try:
        response = client.get(f"/scan/progress/{job_id}")

        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "done"
        assert payload["report_url"] == "/r/test-token"
    finally:
        _scan_jobs.clear()


def test_scan_progress_labels_are_provider_neutral() -> None:
    _scan_jobs.clear()
    job_id = _create_scan_job()
    client = TestClient(app)

    try:
        response = client.get(f"/scan/progress/{job_id}")

        assert response.status_code == 200
        labels = [step["label"] for step in response.json()["steps"]]
        assert "Preparing audit brief" in labels
        assert "Waiting for models to finish" in labels
        assert not any("GPT" in label or "OpenAI" in label for label in labels)
    finally:
        _scan_jobs.clear()


def test_perform_scan_updates_real_progress(monkeypatch, db_session) -> None:
    async def fake_fetch_html(_url: str) -> str:
        return "<main><h1>Useful page copy.</h1><a>Run the audit</a></main>"

    def fake_analyze_page(page, _brand_voice):
        return AuditResult(
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
            voice_summary=["Plain and direct"],
            recommended_next_action="Tighten the proof.",
        )

    monkeypatch.setattr(main, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(main, "analyze_page", fake_analyze_page)
    monkeypatch.setattr(main, "_fetch_robots_rules", lambda _url: main.asyncio.sleep(0, result=_allow_all_robots()))
    _scan_jobs.clear()
    job_id = _create_scan_job()

    try:
        scan = main.asyncio.run(_perform_scan("example.com", "scan", "", "", db_session, job_id))
        payload = main._job_snapshot(_scan_jobs[job_id])

        assert scan.public_token
        assert payload["completed_steps"] == len(payload["steps"])
        assert all(step["status"] == "done" for step in payload["steps"])
    finally:
        _scan_jobs.clear()


def test_perform_scan_site_depth_saves_multiple_pages(monkeypatch, db_session) -> None:
    pages = {
        "https://example.com": """
            <main>
              <h1>Home page copy.</h1>
              <a href="/pricing">Pricing</a>
              <a href="/blog/launch">Launch post</a>
            </main>
        """,
        "https://example.com/pricing": "<main><h1>Pricing page copy.</h1></main>",
        "https://example.com/blog/launch": "<main><h1>Launch post copy.</h1></main>",
    }

    async def fake_fetch_html(url: str) -> str:
        return pages[url]

    def fake_analyze_page(page, _brand_voice):
        return AuditResult(
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
            voice_summary=["Plain and direct"],
            recommended_next_action=f"Tighten {page.url}.",
        )

    monkeypatch.setattr(main, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(main, "analyze_page", fake_analyze_page)
    monkeypatch.setattr(main, "_fetch_robots_rules", lambda _url: main.asyncio.sleep(0, result=_allow_all_robots()))

    scan = main.asyncio.run(_perform_scan("example.com", "site", "", "", db_session))

    assert len(scan.page_results) == 3
    assert [page.url for page in scan.page_results] == [
        "https://example.com",
        "https://example.com/pricing",
        "https://example.com/blog/launch",
    ]


def test_discover_scan_urls_uses_sitemap_before_page_links(monkeypatch) -> None:
    html = """
        <main>
          <a href="/pricing">Pricing</a>
          <a href="/blog/launch">Launch</a>
        </main>
    """

    async def fake_fetch_sitemap_locations(_sitemap_url: str) -> list[str]:
        return [
            "https://example.com/features",
            "https://example.com/blog/from-sitemap",
        ]

    monkeypatch.setattr(main, "_fetch_sitemap_locations", fake_fetch_sitemap_locations)

    urls = main.asyncio.run(
        main._discover_scan_urls(html, "https://example.com", "site", 4, _allow_all_robots())
    )

    assert urls == [
        "https://example.com",
        "https://example.com/features",
        "https://example.com/blog/from-sitemap",
        "https://example.com/pricing",
    ]


def test_perform_scan_stops_when_robots_disallows_start_url(monkeypatch, db_session) -> None:
    async def fake_fetch_html(_url: str) -> str:
        return "<main><h1>Should not fetch.</h1></main>"

    monkeypatch.setattr(main, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(main, "_fetch_robots_rules", lambda _url: main.asyncio.sleep(0, result=_disallow_all_robots()))

    try:
        main.asyncio.run(_perform_scan("example.com", "scan", "", "", db_session))
    except FetchError as exc:
        assert "robots.txt" in str(exc)
    else:
        raise AssertionError("Expected robots.txt disallow to stop the scan")
