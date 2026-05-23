from app.config import get_settings
from app import main
from app.main import _complete_job, _create_scan_job, _perform_scan, _save_scan, _scan_attempts, _scan_jobs
from app.schemas import AuditIssue, AuditResult, ExtractedLine, ExtractedPage, RewriteSuggestion, Scorecard
from app.services.extractor import FetchError
from fastapi.testclient import TestClient
from app.main import app, get_db
from types import SimpleNamespace
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
    assert '<meta name="description" content="Revisi is a brand voice auditor and website copy audit tool' in response.text
    assert '<meta name="robots" content="index, follow">' in response.text
    assert '<link rel="canonical" href="http://testserver/">' in response.text
    assert '<meta property="og:title" content="Revisi - Brand voice auditor for your website">' in response.text
    assert '<meta property="og:url" content="http://testserver/">' in response.text
    assert '<meta name="twitter:card" content="summary">' in response.text


def test_robots_txt_blocks_private_scan_surfaces() -> None:
    client = TestClient(app)
    response = client.get("/robots.txt")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "User-agent: *" in response.text
    assert "Allow: /" in response.text
    assert "Disallow: /scan" in response.text
    assert "Disallow: /scan-sync" in response.text
    assert "Disallow: /scan/progress/" in response.text
    assert "Disallow: /r/" in response.text
    assert "Sitemap: http://testserver/sitemap.xml" in response.text


def test_sitemap_xml_lists_homepage_only() -> None:
    client = TestClient(app)
    response = client.get("/sitemap.xml")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/xml")
    assert "<loc>http://testserver/</loc>" in response.text
    assert "/scan" not in response.text
    assert "/r/" not in response.text


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
    assert "<title>Revisi Audit Report</title>" in response.text
    assert '<meta name="robots" content="noindex, nofollow">' in response.text
    assert "Export PDF" not in response.text
    assert "Share" not in response.text
    assert "Save guides and rewrites" in response.text
    assert "Lower-confidence result" in response.text
    assert "Plain and direct" in response.text
    assert "Brand Fit <small>| 80 / 100</small>" in response.text
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


def test_app_site_scan_returns_job_id(monkeypatch, db_session) -> None:
    async def fake_run_app_scan_job(*_args, **_kwargs):
        return None

    user = main.models.User(id="00000000-0000-4000-8000-000000000020", email="scanjob@example.com")
    site = main.models.Site(user=user, name="Async Site", base_url="https://async.example", domain="async.example")
    db_session.add_all([user, site])
    db_session.commit()
    monkeypatch.setattr(main, "_run_app_scan_job", fake_run_app_scan_job)
    _scan_jobs.clear()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.post(
            f"/app/sites/{site.id}/scan",
            data={"depth": "site"},
            headers={"Accept": "application/json"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 202
    assert response.json()["job_id"] in _scan_jobs
    _scan_jobs.clear()


def test_app_routes_require_login() -> None:
    client = TestClient(app)
    response = client.get("/app", follow_redirects=False)

    assert response.status_code == 303
    assert response.headers["location"] == "/login"


def test_app_site_workspace_lists_owned_sites(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000001", email="editor@example.com")
    other_user = main.models.User(id="00000000-0000-4000-8000-000000000002", email="other@example.com")
    site = main.models.Site(user=user, name="Client Site", base_url="https://client.example", domain="client.example")
    other_site = main.models.Site(user=other_user, name="Other Site", base_url="https://other.example", domain="other.example")
    db_session.add_all([user, other_user, site, other_site])
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(
        id="00000000-0000-4000-8000-000000000001",
        email="editor@example.com",
    )
    client = TestClient(app)

    try:
        response = client.get("/app")
        detail = client.get(f"/app/sites/{other_site.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Your" in response.text
    assert "sites" in response.text
    assert "Add site" in response.text
    assert 'data-add-site-open' in response.text
    assert 'id="add-site-modal"' in response.text
    assert 'data-workspace-rail-toggle' in response.text
    assert 'id="workspace-rail"' in response.text
    assert 'data-app-scan-form' in response.text
    assert 'id="app-scan-loader"' in response.text
    assert "Import sitemap" not in response.text
    assert "Client Site" in response.text
    assert "First scan pending" in response.text
    assert "Other Site" not in response.text
    assert detail.status_code == 404


def test_app_site_detail_renders_latest_pages_table(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000012", email="pages@example.com")
    site = main.models.Site(
        user=user,
        name="SplitPea",
        base_url="https://splitpea.co",
        domain="splitpea.co",
        brand_voice_text="Plainspoken and practical.",
    )
    db_session.add_all([user, site])
    db_session.commit()
    page = ExtractedPage(
        url="https://splitpea.co/pricing",
        title="Pricing",
        meta_description="Pricing page",
        headings=["Pricing"],
        ctas=["Start"],
        lines=[ExtractedLine(source="H1", text="Simple pricing for small teams.")],
    )
    result = AuditResult(
        overall_score=92,
        verdict="Strong, with clear revision targets",
        scoring_context="SaaS pricing page",
        contextual_modifiers=["Message Hierarchy"],
        scores=Scorecard(
            brand_fit=88,
            audience_fit=84,
            clarity=91,
            human_sound=86,
            specificity=82,
            trust=79,
            distinctiveness=76,
        ),
        ai_sludge_risk=18,
        top_issues=[
            AuditIssue(
                issue_type="Too vague",
                priority="Medium",
                source="H1",
                original_copy="Simple pricing for small teams.",
                explanation="Add more proof.",
                suggested_rewrite="Show the plan and who it fits.",
            )
        ],
        line_level_rewrites=[],
        voice_summary=["Plain and direct"],
        recommended_next_action="Tighten the proof.",
    )
    main._save_scan_pages(
        db_session,
        "splitpea.co",
        "https://splitpea.co",
        site.brand_voice_text,
        [(page, result)],
        user=user,
        site=site,
        scan_mode="site",
    )
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.get(f"/app/sites/{site.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "SplitPea" in response.text
    assert "splitpea.co" in response.text
    assert "Pages" in response.text
    assert "Pricing" in response.text
    assert "/pricing" in response.text
    assert "Brand Fit" in response.text
    assert "92" in response.text
    assert "Open &rarr;" in response.text
    assert "/voice" in response.text
    assert "data-site-guide-open" not in response.text
    assert 'id="site-guide-modal"' not in response.text
    assert 'data-app-scan-form' in response.text
    assert 'id="app-scan-loader"' in response.text


def test_app_site_voice_page_renders_per_site_guide_modal(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000013", email="voice@example.com")
    site = main.models.Site(
        user=user,
        name="Voice Site",
        base_url="https://voice.example",
        domain="voice.example",
        brand_voice_text="Plainspoken and specific.",
    )
    db_session.add_all([user, site])
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.get(f"/app/sites/{site.id}/voice")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Your" in response.text
    assert "voice" in response.text
    assert "Voice Site" in response.text
    assert "Plainspoken and specific." in response.text
    assert "data-site-guide-open" in response.text
    assert 'id="site-guide-modal"' in response.text
    assert "brand_voice_file" in response.text


def test_app_site_report_trends_scan_metrics(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000015", email="report@example.com")
    site = main.models.Site(user=user, name="Report Site", base_url="https://report.example", domain="report.example")
    db_session.add_all([user, site])
    db_session.commit()

    def save_report_scan(path: str, overall: int, brand_fit: int, clarity: int) -> None:
        page = ExtractedPage(
            url=f"https://report.example{path}",
            title=f"Page {path}",
            meta_description="Report page",
            headings=["Report"],
            ctas=["Start"],
            lines=[ExtractedLine(source="H1", text="Clear copy for the report.")],
        )
        result = AuditResult(
            overall_score=overall,
            verdict="Clear trend data",
            scoring_context="Site report",
            contextual_modifiers=[],
            scores=Scorecard(
                brand_fit=brand_fit,
                audience_fit=80,
                clarity=clarity,
                human_sound=78,
                specificity=76,
                trust=74,
                distinctiveness=72,
            ),
            ai_sludge_risk=12,
            top_issues=[],
            line_level_rewrites=[],
            voice_summary=["Direct and useful"],
            recommended_next_action="Keep tracking the scan trend.",
        )
        main._save_scan_pages(
            db_session,
            "report.example",
            "https://report.example",
            site.brand_voice_text,
            [(page, result)],
            user=user,
            site=site,
            scan_mode="paid_app",
        )

    save_report_scan("/", 70, 68, 72)
    save_report_scan("/pricing", 86, 88, 90)
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.get(f"/app/sites/{site.id}/report")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "Site" in response.text
    assert "report" in response.text
    assert 'data-site-report-chart' in response.text
    assert 'data-report-metric="overview"' in response.text
    assert 'data-report-metric="brand_fit"' in response.text
    assert "Scan history" in response.text
    assert "86" in response.text
    assert "/voice" in response.text


def test_update_site_guide_accepts_markdown_upload(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000014", email="uploadvoice@example.com")
    site = main.models.Site(user=user, name="Upload Voice", base_url="https://upload.example", domain="upload.example")
    db_session.add_all([user, site])
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.post(
            f"/app/sites/{site.id}/guide",
            data={"brand_voice": "Pasted fallback"},
            files={"brand_voice_file": ("voice.md", b"# Voice\nPrecise and practical.", "text/markdown")},
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    db_session.refresh(site)
    assert response.status_code == 303
    assert response.headers["location"].startswith(f"/app/sites/{site.id}/voice")
    assert site.brand_voice_text == "# Voice\nPrecise and practical."


def test_create_site_accepts_markdown_guide_upload(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000003", email="guide@example.com")
    db_session.add(user)
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.post(
            "/app/sites",
            data={"name": "Guide Site", "url": "guide.example", "brand_voice": "Pasted note"},
            files={"brand_voice_file": ("brand-voice.md", b"# Voice\nPlain and precise.", "text/markdown")},
            follow_redirects=False,
        )
    finally:
        app.dependency_overrides.clear()

    site = db_session.query(main.models.Site).filter(main.models.Site.name == "Guide Site").one()
    assert response.status_code == 303
    assert site.brand_voice_text == "# Voice\nPlain and precise."


def test_create_site_rejects_non_markdown_guide_upload(db_session) -> None:
    user = main.models.User(id="00000000-0000-4000-8000-000000000004", email="unsafe@example.com")
    db_session.add(user)
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[main.get_current_user] = lambda: SimpleNamespace(id=user.id, email=user.email)
    client = TestClient(app)

    try:
        response = client.post(
            "/app/sites",
            data={"name": "Unsafe Site", "url": "unsafe.example"},
            files={"brand_voice_file": ("design.exe", b"MZ executable", "application/octet-stream")},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert "data-add-site-auto-open" in response.text
    assert "must be Markdown .md files" in response.text
    assert db_session.query(main.models.Site).filter(main.models.Site.name == "Unsafe Site").count() == 0


def test_free_scan_ignores_guide_depth_and_rewrites(monkeypatch, db_session) -> None:
    async def fake_fetch_html(_url: str) -> str:
        return "<main><h1>Home copy.</h1><a href='/pricing'>Pricing</a></main>"

    def fake_analyze_page(page, brand_voice, include_rewrites):
        assert brand_voice is None
        assert include_rewrites is False
        return AuditResult(
            overall_score=70,
            verdict="Usable but generic or under-supported",
            scoring_context="General brand copy",
            contextual_modifiers=["Message Hierarchy"],
            scores=Scorecard(
                brand_fit=70,
                audience_fit=70,
                clarity=70,
                human_sound=70,
                specificity=70,
                trust=70,
                distinctiveness=70,
            ),
            ai_sludge_risk=20,
            top_issues=[
                AuditIssue(
                    issue_type="Too vague",
                    priority="High",
                    source="H1",
                    original_copy="Home copy.",
                    explanation="Needs detail.",
                    suggested_rewrite="A paid concrete rewrite.",
                )
            ],
            line_level_rewrites=[
                RewriteSuggestion(
                    source="H1",
                    original="Home copy.",
                    rewrite="A paid concrete rewrite.",
                    reason="More specific.",
                )
            ],
            voice_summary=["Plain and direct"],
            recommended_next_action="Tighten the hero.",
        )

    monkeypatch.setattr(main, "fetch_html", fake_fetch_html)
    monkeypatch.setattr(main, "analyze_page", fake_analyze_page)
    monkeypatch.setattr(main, "_fetch_robots_rules", lambda _url: main.asyncio.sleep(0, result=_allow_all_robots()))

    scan = main.asyncio.run(_perform_scan("example.com", "site", "Private guide", "", db_session, scan_mode="free"))

    assert scan.scan_mode == "free"
    assert scan.brand_voice_text is None
    assert len(scan.page_results) == 1
    assert scan.page_result.rewrites == []
    assert scan.page_result.issues[0].suggested_rewrite == ""


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


def test_perform_scan_uses_firecrawl_for_thin_primary_copy(monkeypatch, db_session) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    get_settings.cache_clear()

    async def fake_fetch_html(_url: str) -> str:
        return "<div id=\"root\"><h1>Hi</h1></div>"

    async def fake_fetch_firecrawl_html(_url: str) -> str:
        return """
            <main>
              <h1>Rendered positioning copy</h1>
              <p>This rendered page explains the product, the buyer, the workflow, and the reason to trust it.</p>
              <p>Teams use it to find vague claims, replace generic language, and keep launch pages on voice.</p>
            </main>
        """

    def fake_analyze_page(page, _brand_voice):
        assert "Rendered positioning copy" in page.combined_text
        assert "Teams use it" in page.combined_text
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
    monkeypatch.setattr(main, "fetch_firecrawl_html", fake_fetch_firecrawl_html)
    monkeypatch.setattr(main, "analyze_page", fake_analyze_page)
    monkeypatch.setattr(main, "_fetch_robots_rules", lambda _url: main.asyncio.sleep(0, result=_allow_all_robots()))

    try:
        scan = main.asyncio.run(_perform_scan("example.com", "scan", "", "", db_session))

        assert "Rendered positioning copy" in scan.page_result.extracted_copy[0]["text"]
    finally:
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        get_settings.cache_clear()


def test_perform_scan_skips_firecrawl_for_enough_primary_copy(monkeypatch, db_session) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "fc-test")
    get_settings.cache_clear()

    async def fake_fetch_html(_url: str) -> str:
        return """
            <main>
              <h1>Clear primary page copy</h1>
              <p>This page has enough server-rendered copy for the primary extractor to audit without fallback.</p>
              <p>It names the buyer, the workflow, the outcome, and the reason the offer matters today.</p>
              <p>It also includes proof, concrete next steps, and enough language to clear the fallback threshold.</p>
              <p>The scanner should keep this page on the fast path and avoid spending a Firecrawl credit.</p>
              <p>This final paragraph keeps the primary extraction over the configured line and word thresholds by adding useful details about the audience, promise, evidence, workflow, comparison points, onboarding path, and next step.</p>
            </main>
        """

    async def fake_fetch_firecrawl_html(_url: str) -> str:
        raise AssertionError("Firecrawl should not run when primary extraction has enough copy.")

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
    monkeypatch.setattr(main, "fetch_firecrawl_html", fake_fetch_firecrawl_html)
    monkeypatch.setattr(main, "analyze_page", fake_analyze_page)
    monkeypatch.setattr(main, "_fetch_robots_rules", lambda _url: main.asyncio.sleep(0, result=_allow_all_robots()))

    try:
        scan = main.asyncio.run(_perform_scan("example.com", "scan", "", "", db_session))

        assert "Clear primary page copy" in scan.page_result.extracted_copy[0]["text"]
    finally:
        monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
        get_settings.cache_clear()


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
