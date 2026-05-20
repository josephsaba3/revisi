import asyncio
from html import escape
from typing import Any

from app.config import get_settings
from app.services.extractor import FetchError


_firecrawl_semaphore: asyncio.Semaphore | None = None
_firecrawl_semaphore_size = 0


async def fetch_firecrawl_html(url: str) -> str:
    settings = get_settings()
    if not settings.firecrawl_api_key:
        raise FetchError("Firecrawl fallback is not configured.")

    async with _get_firecrawl_semaphore():
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(_scrape_firecrawl, url),
                timeout=settings.firecrawl_timeout_seconds,
            )
        except TimeoutError as exc:
            raise FetchError("Firecrawl timed out while rendering that page.") from exc


def _get_firecrawl_semaphore() -> asyncio.Semaphore:
    global _firecrawl_semaphore, _firecrawl_semaphore_size

    settings = get_settings()
    size = max(settings.firecrawl_max_concurrency, 1)
    if _firecrawl_semaphore is None or _firecrawl_semaphore_size != size:
        _firecrawl_semaphore = asyncio.Semaphore(size)
        _firecrawl_semaphore_size = size
    return _firecrawl_semaphore


def _scrape_firecrawl(url: str) -> str:
    try:
        from firecrawl import Firecrawl
    except ImportError as exc:
        raise FetchError("Firecrawl fallback requires the firecrawl-py package.") from exc

    settings = get_settings()
    try:
        client = Firecrawl(api_key=settings.firecrawl_api_key or "")
        result = client.scrape(url, formats=["markdown", "html"])
    except Exception as exc:
        raise FetchError(f"Firecrawl could not render that page: {exc}") from exc

    payload = _unwrap_payload(result)
    html = _get_value(payload, "html")
    if isinstance(html, str) and html.strip():
        return html

    markdown = _get_value(payload, "markdown")
    if isinstance(markdown, str) and markdown.strip():
        return _markdown_to_html(markdown)

    raise FetchError("Firecrawl did not return extractable page content.")


def _unwrap_payload(value: Any) -> Any:
    data = _get_value(value, "data")
    if data is not None:
        return data
    return value


def _get_value(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


def _markdown_to_html(markdown: str) -> str:
    lines = [line.strip(" #*\t") for line in markdown.splitlines()]
    paragraphs = [f"<p>{escape(line)}</p>" for line in lines if line.strip()]
    return f"<main>{''.join(paragraphs)}</main>"
