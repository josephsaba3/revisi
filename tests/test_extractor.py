import pytest

from app.services.extractor import extract_visible_copy, normalize_url


HTML = """
<!doctype html>
<html>
  <head>
    <title>Acme Audit</title>
    <meta name="description" content="A clear page audit for SaaS founders.">
  </head>
  <body>
    <nav>Home Pricing Login</nav>
    <main>
      <h1>Find the copy that costs trust</h1>
      <h2>Page-level feedback</h2>
      <p>Scan a page and see which lines sound generic, vague, or hard to believe.</p>
      <a href="/demo">See a sample audit</a>
      <button>Scan page</button>
    </main>
    <footer>Terms Privacy</footer>
  </body>
</html>
"""


def test_normalize_url_adds_https() -> None:
    assert normalize_url("example.com") == "https://example.com"


def test_normalize_url_rejects_non_http() -> None:
    with pytest.raises(ValueError):
        normalize_url("ftp://example.com")


def test_extract_visible_copy_ignores_boilerplate_and_finds_ctas() -> None:
    page = extract_visible_copy(HTML, "https://example.com")

    assert page.title == "Acme Audit"
    assert page.meta_description == "A clear page audit for SaaS founders."
    assert "Find the copy that costs trust" in page.headings
    assert "See a sample audit" in page.ctas
    assert "Scan page" in page.ctas
    assert all("Terms Privacy" not in line.text for line in page.lines)


def test_extract_visible_copy_handles_missing_title_meta() -> None:
    page = extract_visible_copy("<main><h1>Hello</h1><p>Useful page copy lives here.</p></main>", "https://example.com")

    assert page.title is None
    assert page.meta_description is None
    assert page.lines
