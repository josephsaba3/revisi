# Brand Voice Auditor SaaS MVP

FastAPI/Jinja MVP for scanning one URL, extracting visible copy, scoring brand voice and clarity, and returning page-level issues with line-level rewrites.

## Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:OPENAI_API_KEY="your-key"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`.

If `DATABASE_URL` is not set, the app uses `sqlite:///./brand_voice_auditor.db`. Use a Postgres URL for production-like storage.

## Test

```powershell
python -m pytest
```
