from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.schemas import ExtractedLine, ExtractedPage


CONTENT_SELECTORS = ["h1", "h2", "h3", "p", "li", "blockquote", "button", "a"]
BOILERPLATE_SELECTORS = [
    "script",
    "style",
    "noscript",
    "svg",
    "nav",
    "footer",
    "header",
    "form",
    "[aria-hidden='true']",
]
CTA_WORDS = ("book", "start", "try", "get", "buy", "sign", "join", "contact", "demo", "audit", "scan", "upload")


class FetchError(Exception):
    pass


def normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise ValueError("Enter a URL to scan.")
    if "://" not in raw_url:
        raw_url = f"https://{raw_url}"

    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Enter a valid http or https URL.")
    return raw_url


async def fetch_html(url: str) -> str:
    settings = get_settings()
    headers = {
        "User-Agent": "BrandVoiceAuditor/0.1 (+https://splitpea.example)",
        "Accept": "text/html,application/xhtml+xml",
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=settings.request_timeout_seconds) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise FetchError(f"Could not fetch that page: {exc}") from exc

    content_type = response.headers.get("content-type", "")
    if "html" not in content_type.lower() and "<html" not in response.text[:500].lower():
        raise FetchError("That URL did not return an HTML page.")
    return response.text


def extract_visible_copy(html: str, url: str) -> ExtractedPage:
    soup = BeautifulSoup(html, "lxml")
    for selector in BOILERPLATE_SELECTORS:
        for element in soup.select(selector):
            element.decompose()

    title = _clean_text(soup.title.string if soup.title else "")
    meta_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = _clean_text(meta_tag.get("content", "")) if meta_tag else None

    headings = [_clean_text(node.get_text(" ", strip=True)) for node in soup.select("h1, h2")]
    headings = _dedupe([heading for heading in headings if heading])

    lines: list[ExtractedLine] = []
    ctas: list[str] = []
    seen: set[str] = set()

    for node in soup.select(",".join(CONTENT_SELECTORS)):
        text = _clean_text(node.get_text(" ", strip=True))
        if not _is_meaningful(text) or text in seen:
            continue
        seen.add(text)

        source = node.name.upper()
        if node.name in {"button", "a"} and _looks_like_cta(text):
            ctas.append(text)
            source = "CTA"
        lines.append(ExtractedLine(source=source, text=text))

    return ExtractedPage(
        url=url,
        title=title or None,
        meta_description=meta_description or None,
        headings=headings[:12],
        ctas=_dedupe(ctas)[:12],
        lines=lines[:120],
    )


def _clean_text(text: str | None) -> str:
    return " ".join((text or "").split()).strip()


def _is_meaningful(text: str) -> bool:
    if len(text) < 3:
        return False
    if len(text.split()) == 1 and len(text) < 12:
        return False
    return True


def _looks_like_cta(text: str) -> bool:
    lowered = text.lower()
    return len(text.split()) <= 9 and any(word in lowered for word in CTA_WORDS)


def _dedupe(values: list[str]) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            output.append(value)
    return output
