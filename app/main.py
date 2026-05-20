from contextlib import asynccontextmanager
import asyncio
from html import escape
import logging
import xml.etree.ElementTree as ET
from urllib import robotparser
import time
from urllib.parse import urljoin, urlparse, urlunparse
from uuid import uuid4

from bs4 import BeautifulSoup
import httpx
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models
from .config import get_settings
from .database import SessionLocal, get_db, init_db
from .schemas import AuditResult
from .services.analyzer import analyze_page
from .services.extractor import FetchError, extract_visible_copy, fetch_html, normalize_url
from .services.phrase_flags import find_phrase_flags


logger = logging.getLogger(__name__)
CRAWLER_USER_AGENT = "BrandVoiceAuditor/0.1"
DEFAULT_SEO_TITLE = "Revisi - Brand voice auditor for your website"
DEFAULT_SEO_DESCRIPTION = (
    "Revisi is a brand voice auditor and website copy audit tool for marketers, founders, "
    "and agencies who need clearer, more on-brand website copy."
)
_scan_attempts: dict[str, list[float]] = {}
_scan_jobs: dict[str, dict] = {}
_scan_job_ttl_seconds = 1800
_scan_steps = [
    {"key": "validate", "label": "Checking the URL"},
    {"key": "guide", "label": "Reading the design guide"},
    {"key": "fetch", "label": "Fetching the page"},
    {"key": "extract", "label": "Stripping chrome and extracting copy"},
    {"key": "phrases", "label": "Cross-referencing AI tell-words"},
    {"key": "brief", "label": "Preparing audit brief"},
    {"key": "models", "label": "Waiting for models to finish"},
    {"key": "ground", "label": "Checking quotes against page copy"},
    {"key": "score", "label": "Recomputing score and verdict"},
    {"key": "save", "label": "Generating the report"},
    {"key": "finish", "label": "Opening the report"},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Brand Voice Auditor", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "index.html",
        {"seo": _seo_context(request)},
    )


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt(request: Request) -> PlainTextResponse:
    sitemap_url = _absolute_url(request, "/sitemap.xml")
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /scan",
            "Disallow: /scan-sync",
            "Disallow: /scan/progress/",
            "Disallow: /r/",
            f"Sitemap: {sitemap_url}",
            "",
        ]
    )
    return PlainTextResponse(body, media_type="text/plain")


@app.get("/sitemap.xml")
def sitemap_xml(request: Request) -> Response:
    home_url = escape(_absolute_url(request, "/"), quote=True)
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{home_url}</loc>\n"
        "  </url>\n"
        "</urlset>\n"
    )
    return Response(body, media_type="application/xml")


@app.post("/scan")
async def scan(
    request: Request,
    background_tasks: BackgroundTasks,
    url: str = Form(...),
    depth: str = Form("scan"),
    brand_voice: str = Form(""),
    brand_voice_file: UploadFile | None = File(None),
) -> JSONResponse:
    if _scan_rate_limited(request):
        return JSONResponse(
            {"error": "Too many scans from this connection. Try again soon."},
            status_code=429,
        )

    uploaded_voice = await _read_brand_voice_file(brand_voice_file)
    job_id = _create_scan_job()
    background_tasks.add_task(_run_scan_job, job_id, url, depth, brand_voice, uploaded_voice)
    return JSONResponse({"job_id": job_id}, status_code=202)


@app.get("/scan/progress/{job_id}")
def scan_progress(job_id: str) -> JSONResponse:
    job = _scan_jobs.get(job_id)
    if not job:
        return JSONResponse({"error": "Scan job not found."}, status_code=404)
    return JSONResponse(_job_snapshot(job))


@app.post("/scan-sync", response_class=HTMLResponse)
async def scan_sync(
    request: Request,
    url: str = Form(...),
    depth: str = Form("scan"),
    brand_voice: str = Form(""),
    brand_voice_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    if _scan_rate_limited(request):
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "seo": _seo_context(request),
                "error": "Too many scans from this connection. Try again soon.",
                "url": url,
                "brand_voice": brand_voice,
            },
            status_code=429,
        )

    try:
        uploaded_voice = await _read_brand_voice_file(brand_voice_file)
        scan_model = await _perform_scan(url, depth, brand_voice, uploaded_voice, db)
    except (ValueError, FetchError, RuntimeError) as exc:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"seo": _seo_context(request), "error": str(exc), "url": url, "brand_voice": brand_voice},
            status_code=400,
        )
    except Exception as exc:
        logger.exception("Scan failed unexpectedly")
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "error": "The scan failed unexpectedly. Check the deployment logs for the Python traceback.",
                "seo": _seo_context(request),
                "url": url,
                "brand_voice": brand_voice,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request,
        "result.html",
        _result_template_context(scan_model)
        | {"seo": _seo_context(request, title="Revisi Audit Report", robots="noindex, nofollow")},
    )


@app.get("/r/{public_token}", response_class=HTMLResponse)
def result(request: Request, public_token: str, page_id: int | None = None, db: Session = Depends(get_db)) -> HTMLResponse:
    scan_model = db.query(models.Scan).filter(models.Scan.public_token == public_token).first()
    if not scan_model:
        raise HTTPException(status_code=404, detail="Scan not found")
    return templates.TemplateResponse(
        request,
        "result.html",
        _result_template_context(scan_model, page_id=page_id)
        | {"seo": _seo_context(request, title="Revisi Audit Report", robots="noindex, nofollow")},
    )


def _public_site_url(request: Request) -> str:
    configured_url = get_settings().public_site_url
    if configured_url:
        return configured_url.rstrip("/")
    return f"{request.url.scheme}://{request.url.netloc}".rstrip("/")


def _absolute_url(request: Request, path: str = "/") -> str:
    normalized_path = path if path.startswith("/") else f"/{path}"
    return f"{_public_site_url(request)}{normalized_path}"


def _seo_context(
    request: Request,
    *,
    title: str = DEFAULT_SEO_TITLE,
    description: str = DEFAULT_SEO_DESCRIPTION,
    path: str | None = "/",
    robots: str = "index, follow",
    og_type: str = "website",
) -> dict[str, str]:
    canonical_path = request.url.path if path is None else path
    return {
        "title": title,
        "description": description,
        "robots": robots,
        "canonical_url": _absolute_url(request, canonical_path),
        "og_type": og_type,
    }


def _client_rate_limit_key(request: Request) -> str:
    cf_ip = request.headers.get("CF-Connecting-IP")
    if cf_ip:
        return cf_ip.strip()

    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()

    if request.client and request.client.host:
        return request.client.host

    return "unknown"


def _scan_rate_limited(request: Request) -> bool:
    settings = get_settings()
    if not settings.scan_rate_limit_enabled:
        return False

    now = time.monotonic()
    window = settings.scan_rate_limit_window_seconds
    limit = settings.scan_rate_limit_count
    key = _client_rate_limit_key(request)
    cutoff = now - window

    attempts = [stamp for stamp in _scan_attempts.get(key, []) if stamp > cutoff]
    if len(attempts) >= limit:
        _scan_attempts[key] = attempts
        return True

    attempts.append(now)
    _scan_attempts[key] = attempts
    return False


async def _read_brand_voice_file(file: UploadFile | None) -> str:
    if not file or not file.filename:
        return ""
    contents = await file.read()
    return contents.decode("utf-8", errors="ignore")


async def _perform_scan(
    submitted_url: str,
    depth: str,
    brand_voice: str,
    uploaded_voice: str,
    db: Session,
    job_id: str | None = None,
) -> models.Scan:
    _start_job_step(job_id, "validate")
    normalized_url = normalize_url(submitted_url)
    scan_depth = _normalize_scan_depth(depth)
    _finish_job_step(job_id, "validate")

    _start_job_step(job_id, "guide")
    brand_voice_text = (uploaded_voice or brand_voice or "").strip() or None
    _finish_job_step(job_id, "guide")

    _start_job_step(job_id, "fetch")
    robots = await _fetch_robots_rules(normalized_url)
    if not _robots_can_fetch(robots, normalized_url):
        raise FetchError("That site's robots.txt does not allow Revisi to scan the submitted URL.")
    html = await fetch_html(normalized_url)
    _finish_job_step(job_id, "fetch")

    _start_job_step(job_id, "extract")
    page_limit = _scan_page_limit(scan_depth)
    pages = [extract_visible_copy(html, normalized_url)]
    if page_limit > 1:
        discovered_urls = await _discover_scan_urls(html, normalized_url, scan_depth, page_limit, robots)
        for page_url in discovered_urls[1:]:
            if not _robots_can_fetch(robots, page_url):
                continue
            try:
                page_html = await fetch_html(page_url)
            except FetchError:
                continue
            pages.append(extract_visible_copy(page_html, page_url))
            if len(pages) >= page_limit:
                break
    _finish_job_step(job_id, "extract")

    _start_job_step(job_id, "phrases")
    for page in pages:
        find_phrase_flags(page.combined_text)
    _finish_job_step(job_id, "phrases")

    _start_job_step(job_id, "brief")
    _finish_job_step(job_id, "brief")

    _start_job_step(job_id, "models")
    results = [
        await asyncio.to_thread(analyze_page, page, brand_voice_text)
        for page in pages
    ]
    _finish_job_step(job_id, "models")

    _start_job_step(job_id, "ground")
    _finish_job_step(job_id, "ground")

    _start_job_step(job_id, "score")
    _finish_job_step(job_id, "score")

    _start_job_step(job_id, "save")
    scan_model = _save_scan_pages(db, submitted_url, normalized_url, brand_voice_text, list(zip(pages, results)))
    _finish_job_step(job_id, "save")

    _start_job_step(job_id, "finish")
    _finish_job_step(job_id, "finish")
    return scan_model


async def _run_scan_job(job_id: str, url: str, depth: str, brand_voice: str, uploaded_voice: str) -> None:
    _mark_job_running(job_id)
    db = SessionLocal()
    try:
        scan_model = await _perform_scan(url, depth, brand_voice, uploaded_voice, db, job_id)
        _complete_job(job_id, f"/r/{scan_model.public_token}")
    except (ValueError, FetchError, RuntimeError) as exc:
        _fail_job(job_id, str(exc))
    except Exception:
        logger.exception("Scan job failed unexpectedly")
        _fail_job(job_id, "The scan failed unexpectedly. Check the deployment logs for the Python traceback.")
    finally:
        db.close()


def _create_scan_job() -> str:
    _prune_scan_jobs()
    job_id = uuid4().hex
    now = time.time()
    _scan_jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "created_at": now,
        "updated_at": now,
        "started_at": None,
        "finished_at": None,
        "report_url": None,
        "error": None,
        "steps": [
            {
                "key": step["key"],
                "label": step["label"],
                "status": "pending",
                "started_at": None,
                "completed_at": None,
            }
            for step in _scan_steps
        ],
    }
    return job_id


def _mark_job_running(job_id: str | None) -> None:
    if not job_id or job_id not in _scan_jobs:
        return
    now = time.time()
    _scan_jobs[job_id]["status"] = "running"
    _scan_jobs[job_id]["started_at"] = now
    _scan_jobs[job_id]["updated_at"] = now


def _start_job_step(job_id: str | None, step_key: str) -> None:
    if not job_id or job_id not in _scan_jobs:
        return
    now = time.time()
    job = _scan_jobs[job_id]
    job["status"] = "running"
    job["updated_at"] = now
    for step in job["steps"]:
        if step["key"] == step_key:
            step["status"] = "running"
            step["started_at"] = step["started_at"] or now
            return


def _finish_job_step(job_id: str | None, step_key: str) -> None:
    if not job_id or job_id not in _scan_jobs:
        return
    now = time.time()
    job = _scan_jobs[job_id]
    job["updated_at"] = now
    for step in job["steps"]:
        if step["key"] == step_key:
            step["status"] = "done"
            step["completed_at"] = now
            return


def _complete_job(job_id: str, report_url: str) -> None:
    if job_id not in _scan_jobs:
        return
    now = time.time()
    job = _scan_jobs[job_id]
    job["status"] = "done"
    job["report_url"] = report_url
    job["finished_at"] = now
    job["updated_at"] = now


def _fail_job(job_id: str, error: str) -> None:
    if job_id not in _scan_jobs:
        return
    now = time.time()
    job = _scan_jobs[job_id]
    job["status"] = "error"
    job["error"] = error
    job["finished_at"] = now
    job["updated_at"] = now
    for step in job["steps"]:
        if step["status"] == "running":
            step["status"] = "error"
            step["completed_at"] = now


def _job_snapshot(job: dict) -> dict:
    now = time.time()
    steps = []
    for step in job["steps"]:
        started_at = step["started_at"]
        completed_at = step["completed_at"]
        elapsed = None
        if started_at and completed_at:
            elapsed = round(completed_at - started_at, 1)
        elif started_at and step["status"] == "running":
            elapsed = round(now - started_at, 1)
        steps.append(
            {
                "key": step["key"],
                "label": step["label"],
                "status": step["status"],
                "elapsed_seconds": elapsed,
            }
        )

    current_step = next((step for step in steps if step["status"] in {"running", "error"}), None)
    completed_steps = sum(1 for step in steps if step["status"] == "done")
    elapsed_seconds = round(now - job["created_at"], 1)
    if job["finished_at"]:
        elapsed_seconds = round(job["finished_at"] - job["created_at"], 1)

    return {
        "job_id": job["job_id"],
        "status": job["status"],
        "current_step": current_step,
        "completed_steps": completed_steps,
        "steps": steps,
        "elapsed_seconds": elapsed_seconds,
        "report_url": job["report_url"],
        "error": job["error"],
    }


def _prune_scan_jobs() -> None:
    cutoff = time.time() - _scan_job_ttl_seconds
    stale = [
        job_id
        for job_id, job in _scan_jobs.items()
        if job.get("finished_at") and job["finished_at"] < cutoff
    ]
    for job_id in stale:
        _scan_jobs.pop(job_id, None)


def _normalize_scan_depth(depth: str) -> str:
    return depth if depth in {"scan", "site", "deep"} else "scan"


def _scan_page_limit(depth: str) -> int:
    if depth == "deep":
        return 25
    if depth == "site":
        return 10
    return 1


async def _discover_scan_urls(
    html: str,
    base_url: str,
    depth: str,
    limit: int,
    robots: robotparser.RobotFileParser,
) -> list[str]:
    base = _canonical_page_url(base_url)
    urls = [base]
    seen = {base}
    sitemap_urls = await _discover_sitemap_urls(base, depth, limit, robots)
    for candidate in sitemap_urls:
        if candidate in seen or not _same_site_url(base, candidate):
            continue
        if _looks_like_binary_or_utility_url(urlparse(candidate).path):
            continue
        if not _robots_can_fetch(robots, candidate):
            continue
        urls.append(candidate)
        seen.add(candidate)
        if len(urls) >= limit:
            return urls

    soup = BeautifulSoup(html, "lxml")

    candidates = []
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        candidate = _canonical_page_url(urljoin(base, href))
        if not candidate or candidate in seen:
            continue
        if not _same_site_url(base, candidate):
            continue
        parsed = urlparse(candidate)
        if _looks_like_binary_or_utility_url(parsed.path):
            continue
        if not _robots_can_fetch(robots, candidate):
            continue
        candidates.append(candidate)
        seen.add(candidate)

    candidates.sort(key=lambda url: _scan_url_priority(url, depth))
    urls.extend(candidates[: max(limit - len(urls), 0)])
    return urls


async def _fetch_robots_rules(base_url: str) -> robotparser.RobotFileParser:
    robots_url = urljoin(base_url, "/robots.txt")
    parser = robotparser.RobotFileParser()
    parser.set_url(robots_url)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
            response = await client.get(robots_url, headers={"User-Agent": CRAWLER_USER_AGENT})
        if response.status_code == 404:
            parser.parse([])
        else:
            response.raise_for_status()
            parser.parse(response.text.splitlines())
    except httpx.HTTPError:
        parser.parse([])
    return parser


def _robots_can_fetch(robots: robotparser.RobotFileParser, url: str) -> bool:
    return robots.can_fetch(CRAWLER_USER_AGENT, url)


async def _discover_sitemap_urls(
    base_url: str,
    depth: str,
    limit: int,
    robots: robotparser.RobotFileParser,
) -> list[str]:
    sitemap_urls = list(robots.site_maps() or [])
    default_sitemap = urljoin(base_url, "/sitemap.xml")
    if default_sitemap not in sitemap_urls:
        sitemap_urls.append(default_sitemap)

    discovered: list[str] = []
    seen: set[str] = set()
    for sitemap_url in sitemap_urls[:4]:
        for candidate in await _fetch_sitemap_locations(sitemap_url):
            if candidate in seen:
                continue
            seen.add(candidate)
            if candidate.lower().endswith(".xml"):
                for nested_candidate in await _fetch_sitemap_locations(candidate):
                    if nested_candidate not in seen:
                        seen.add(nested_candidate)
                        discovered.append(_canonical_page_url(nested_candidate))
            else:
                discovered.append(_canonical_page_url(candidate))
            if len(discovered) >= limit * 3:
                break
        if len(discovered) >= limit * 3:
            break

    discovered = [url for url in discovered if url]
    discovered.sort(key=lambda url: _scan_url_priority(url, depth))
    return discovered[: max(limit - 1, 0)]


async def _fetch_sitemap_locations(sitemap_url: str) -> list[str]:
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=8) as client:
            response = await client.get(sitemap_url, headers={"User-Agent": CRAWLER_USER_AGENT})
        if response.status_code == 404:
            return []
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        return []

    locations = []
    for node in root.iter():
        if node.tag.endswith("loc") and node.text:
            locations.append(node.text.strip())
    return locations


def _same_site_url(base_url: str, candidate_url: str) -> bool:
    base = urlparse(base_url)
    candidate = urlparse(candidate_url)
    return (
        candidate.scheme in {"http", "https"}
        and candidate.netloc.lower() == base.netloc.lower()
    )


def _canonical_page_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    path = parsed.path or ""
    if path != "/":
        path = path.rstrip("/")
    else:
        path = ""
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def _looks_like_binary_or_utility_url(path: str) -> bool:
    lowered = path.lower()
    blocked_suffixes = (
        ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".zip", ".mp4", ".mov",
        ".css", ".js", ".ico", ".xml", ".json",
    )
    blocked_parts = ("/cdn-cgi/", "/wp-json/", "/feed", "/tag/", "/author/")
    return lowered.endswith(blocked_suffixes) or any(part in lowered for part in blocked_parts)


def _scan_url_priority(url: str, depth: str) -> tuple[int, int, str]:
    path = urlparse(url).path.lower()
    is_blog = any(part in path for part in ("/blog", "/articles", "/resources", "/guides"))
    if depth == "deep":
        return (0 if is_blog else 1, path.count("/"), path)
    return (1 if is_blog else 0, path.count("/"), path)


def _save_scan(
    db: Session,
    submitted_url: str,
    normalized_url: str,
    brand_voice_text: str | None,
    page,
    result: AuditResult,
) -> models.Scan:
    return _save_scan_pages(db, submitted_url, normalized_url, brand_voice_text, [(page, result)])


def _save_scan_pages(
    db: Session,
    submitted_url: str,
    normalized_url: str,
    brand_voice_text: str | None,
    page_results: list[tuple[object, AuditResult]],
) -> models.Scan:
    scan_model = models.Scan(
        submitted_url=submitted_url,
        normalized_url=normalized_url,
        brand_voice_source="provided" if brand_voice_text else "inferred voice, not confirmed",
        brand_voice_text=brand_voice_text,
    )
    scan_model.page_results = []
    for page, result in page_results:
        page_model = models.PageResult(
            url=page.url,
            title=page.title,
            meta_description=page.meta_description,
            headings=page.headings,
            ctas=page.ctas,
            extracted_copy=[line.model_dump() for line in page.lines],
            overall_score=result.overall_score,
            verdict=result.verdict,
            scoring_context=result.scoring_context,
            contextual_modifiers=result.contextual_modifiers,
            scores=result.scores.model_dump(),
            ai_sludge_risk=result.ai_sludge_risk,
            voice_summary=result.voice_summary,
            recommended_next_action=result.recommended_next_action,
            raw_result=result.model_dump(),
        )
        page_model.issues = [
            models.Issue(
                issue_type=issue.issue_type,
                priority=issue.priority,
                source=issue.source,
                line_id=issue.line_id,
                original_copy=issue.original_copy,
                explanation=issue.explanation,
                suggested_rewrite=issue.suggested_rewrite,
            )
            for issue in result.top_issues
        ]
        page_model.rewrites = [
            models.Rewrite(
                source=rewrite.source,
                line_id=rewrite.line_id,
                original=rewrite.original,
                rewrite=rewrite.rewrite,
                reason=rewrite.reason,
            )
            for rewrite in result.line_level_rewrites
        ]
        scan_model.page_results.append(page_model)
    db.add(scan_model)
    db.commit()
    db.refresh(scan_model)
    return scan_model


def _result_template_context(scan_model: models.Scan, page_id: int | None = None) -> dict:
    pages = list(scan_model.page_results or [])
    if not pages:
        raise HTTPException(status_code=404, detail="Scan has no page results")
    page = next((candidate for candidate in pages if candidate.id == page_id), pages[0])
    extracted_text = "\n".join(
        line.get("text", "") for line in (page.extracted_copy or []) if isinstance(line, dict)
    )
    slop_terms = find_phrase_flags(extracted_text)
    score_map = page.scores or {}
    metric_rows = [
        {
            "label": "Brand Fit",
            "key": "brand_fit",
            "value": score_map.get("brand_fit", 0),
            "desc": "How closely the page matches the intended voice and avoids tone drift.",
        },
        {
            "label": "Audience Fit",
            "key": "audience_fit",
            "value": score_map.get("audience_fit", 0),
            "desc": "Whether the copy speaks to the right reader, situation, and buying stage.",
        },
        {
            "label": "Clarity",
            "key": "clarity",
            "value": score_map.get("clarity", 0),
            "desc": "How quickly a reader can understand the offer, value, and next step.",
        },
        {
            "label": "Human Sound",
            "key": "human_sound",
            "value": score_map.get("human_sound", 0),
            "desc": "Whether the copy feels natural, specific, and free of generated polish.",
        },
        {
            "label": "Specificity",
            "key": "specificity",
            "value": score_map.get("specificity", 0),
            "desc": "How much concrete detail, proof, workflow, or real-world texture is present.",
        },
        {
            "label": "Trust",
            "key": "trust",
            "value": score_map.get("trust", 0),
            "desc": "Whether claims feel supported, transparent, and believable.",
        },
        {
            "label": "Distinctiveness",
            "key": "distinctiveness",
            "value": score_map.get("distinctiveness", 0),
            "desc": "How hard the page is to confuse with another brand in the same category.",
        },
    ]
    word_count = len(extracted_text.split())
    sentence_count = extracted_text.count(".") + extracted_text.count("?") + extracted_text.count("!")
    fallback_notice = next(
        (note for note in (page.voice_summary or []) if "OpenAI" in note and "local draft checker" in note),
        None,
    )
    return {
        "scan": scan_model,
        "page": page,
        "pages": pages,
        "site_score": round(sum(item.overall_score for item in pages) / len(pages)),
        "issues": page.issues,
        "rewrites": page.rewrites,
        "slop_terms": slop_terms,
        "metric_rows": metric_rows,
        "word_count": word_count,
        "sentence_count": sentence_count,
        "fallback_notice": fallback_notice,
    }
