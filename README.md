# Brand Voice Auditor SaaS MVP

FastAPI/Jinja MVP for scanning one URL, extracting visible copy, scoring brand voice and clarity, and returning page-level issues with line-level rewrites.
 
## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY="your-key"
$env:OPENAI_MODEL="gpt-5.5"
$env:OPENAI_REASONING_EFFORT="low"
$env:LLM_ANALYSIS_PROMPT="paste-your-private-analysis-prompt"
$env:FIRECRAWL_API_KEY="fc-your-key"  # optional JS-rendered page fallback
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

If `DATABASE_URL` is not set, the app uses `sqlite:///./brand_voice_auditor.db`. Use a Postgres URL for production-like storage.

Copy `.env.example` to `.env` for a local file-based setup. Keep the full audit prompt in `LLM_ANALYSIS_PROMPT`; it is only sent to the selected model and is not rendered in the report. `OPENAI_ANALYSIS_PROMPT` remains supported as a legacy OpenAI prompt fallback.

The homepage and `/r/{token}` report path stay public for free one-page diagnostic scans. The paid workspace starts at `/app`, with Supabase-backed account screens at `/signup` and `/login`. Configure `SESSION_SECRET`, `PUBLIC_SITE_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, and `TURNSTILE_SITE_KEY` before using the account flow. Supabase Auth must allow the configured `/auth/callback` URL. Revisi forwards the Turnstile token to Supabase on signup and password login.

To make Anthropic primary, set `LLM_PROVIDER=anthropic`, fill `ANTHROPIC_API_KEY`, and leave `ANTHROPIC_MODEL=claude-sonnet-4-6` for the first pass. Keep `OPENAI_API_KEY` set as well if you want Revisi to fall back to GPT when the Anthropic request fails or returns no structured result. Revisi sends the same extracted payload and expects the same structured `AuditResult` response from either provider.

Anthropic effort is set explicitly with `ANTHROPIC_EFFORT=medium` for the default Sonnet 4.6 test path. Change it to `low`, `high`, or `max` to compare the speed, cost, and audit-quality tradeoff. If you switch to Haiku 4.5 with `ANTHROPIC_MODEL=claude-haiku-4-5-20251001`, leave `ANTHROPIC_EFFORT=` blank so Revisi omits the unsupported effort field.

Anthropic prompt caching is enabled by default with `ANTHROPIC_PROMPT_CACHE_ENABLED=true`. This can help repeated scans reuse an identical prompt prefix during tests; it does not reduce the time Claude spends generating the audit output. Set it to `false` for uncached comparisons.

Anthropic-to-OpenAI fallback is enabled by default with `ANTHROPIC_OPENAI_FALLBACK_ENABLED=true`. Set it to `false` when you want Anthropic failures to go straight to the local draft checker instead. If `LLM_PROVIDER=openai`, Revisi still uses OpenAI directly.

On the VPS, set `OPENAI_REASONING_EFFORT=low` in the service environment to keep GPT-5.5 audits cheaper and faster by default when OpenAI is selected or used as the Anthropic fallback.

Revisi uses its fast `httpx` fetch first. If the extracted copy is very light and `FIRECRAWL_API_KEY` is set, it retries that page through Firecrawl so JavaScript-rendered websites can still be audited. Tune `FIRECRAWL_MIN_EXTRACTED_LINES`, `FIRECRAWL_MIN_EXTRACTED_WORDS`, `FIRECRAWL_TIMEOUT_SECONDS`, and `FIRECRAWL_MAX_CONCURRENCY` in `.env` if needed.

## Test

```powershell
python -m pytest
```
