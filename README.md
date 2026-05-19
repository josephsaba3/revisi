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
$env:OPENAI_ANALYSIS_PROMPT="paste-your-private-analysis-prompt"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

If `DATABASE_URL` is not set, the app uses `sqlite:///./brand_voice_auditor.db`. Use a Postgres URL for production-like storage.

Copy `.env.example` to `.env` for a local file-based setup. Keep the full audit prompt in `OPENAI_ANALYSIS_PROMPT`; it is only sent to the model and is not rendered in the report. On the VPS, set `OPENAI_REASONING_EFFORT=low` in the service environment to keep GPT-5.5 audits cheaper and faster by default.

## Test

```powershell
python -m pytest
```
