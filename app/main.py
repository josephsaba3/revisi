from contextlib import asynccontextmanager
import logging

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import models
from .database import get_db, init_db
from .schemas import AuditResult
from .services.analyzer import analyze_page
from .services.extractor import FetchError, extract_visible_copy, fetch_html, normalize_url
from .services.phrase_flags import find_phrase_flags


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Brand Voice Auditor", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "index.html", {})


@app.post("/scan", response_class=HTMLResponse)
async def scan(
    request: Request,
    url: str = Form(...),
    brand_voice: str = Form(""),
    brand_voice_file: UploadFile | None = File(None),
    db: Session = Depends(get_db),
) -> HTMLResponse:
    try:
        normalized_url = normalize_url(url)
        uploaded_voice = await _read_brand_voice_file(brand_voice_file)
        brand_voice_text = (uploaded_voice or brand_voice or "").strip() or None
        html = await fetch_html(normalized_url)
        page = extract_visible_copy(html, normalized_url)
        result = analyze_page(page, brand_voice_text)
        scan_model = _save_scan(db, url, normalized_url, brand_voice_text, page, result)
    except (ValueError, FetchError, RuntimeError) as exc:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"error": str(exc), "url": url, "brand_voice": brand_voice},
            status_code=400,
        )
    except Exception as exc:
        logger.exception("Scan failed unexpectedly")
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "error": "The scan failed unexpectedly. Check the deployment logs for the Python traceback.",
                "url": url,
                "brand_voice": brand_voice,
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request,
        "result.html",
        _result_template_context(scan_model),
    )


@app.get("/r/{public_token}", response_class=HTMLResponse)
def result(request: Request, public_token: str, db: Session = Depends(get_db)) -> HTMLResponse:
    scan_model = db.query(models.Scan).filter(models.Scan.public_token == public_token).first()
    if not scan_model:
        raise HTTPException(status_code=404, detail="Scan not found")
    return templates.TemplateResponse(
        request,
        "result.html",
        _result_template_context(scan_model),
    )


async def _read_brand_voice_file(file: UploadFile | None) -> str:
    if not file or not file.filename:
        return ""
    contents = await file.read()
    return contents.decode("utf-8", errors="ignore")


def _save_scan(
    db: Session,
    submitted_url: str,
    normalized_url: str,
    brand_voice_text: str | None,
    page,
    result: AuditResult,
) -> models.Scan:
    scan_model = models.Scan(
        submitted_url=submitted_url,
        normalized_url=normalized_url,
        brand_voice_source="provided" if brand_voice_text else "inferred voice, not confirmed",
        brand_voice_text=brand_voice_text,
    )
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
            original_copy=issue.original_copy,
            explanation=issue.explanation,
            suggested_rewrite=issue.suggested_rewrite,
        )
        for issue in result.top_issues
    ]
    page_model.rewrites = [
        models.Rewrite(
            source=rewrite.source,
            original=rewrite.original,
            rewrite=rewrite.rewrite,
            reason=rewrite.reason,
        )
        for rewrite in result.line_level_rewrites
    ]
    scan_model.page_result = page_model
    db.add(scan_model)
    db.commit()
    db.refresh(scan_model)
    return scan_model


def _result_template_context(scan_model: models.Scan) -> dict:
    page = scan_model.page_result
    extracted_text = "\n".join(
        line.get("text", "") for line in (page.extracted_copy or []) if isinstance(line, dict)
    )
    slop_terms = find_phrase_flags(extracted_text)
    return {
        "scan": scan_model,
        "page": page,
        "issues": page.issues,
        "rewrites": page.rewrites,
        "slop_terms": slop_terms,
    }
