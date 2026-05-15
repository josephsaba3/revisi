# Deploy to Cloudflare Containers

This repo runs the FastAPI app in a Cloudflare Container and uses a small Worker as the public entrypoint.

## Prerequisites

- Docker Desktop running locally
- Node.js/npm
- Cloudflare account with Workers/Containers enabled
- A managed Postgres database URL

## One-Time Setup

Cloudflare's Node dependencies are much happier outside Google Drive / OneDrive-style synced folders. If `npm install` throws `EBADF`, `EPERM`, or lots of `TAR_ENTRY_ERROR` warnings, clone or copy this repo to a normal local path such as `C:\dev\brand-voice-auditor` before running the npm commands.

```powershell
npm install
npx wrangler login
npx wrangler secret put OPENAI_API_KEY
npx wrangler secret put DATABASE_URL
```

Optional:

```powershell
npx wrangler secret put OPENAI_MODEL
```

Use an external Postgres URL for `DATABASE_URL`. Do not rely on the container filesystem for production data.

## Deploy

```powershell
npx wrangler deploy
```

Wrangler will build the Docker image, push it to Cloudflare's registry, deploy the Worker, and wire requests to the container.

Cloudflare notes that first deploys can take several minutes before containers are ready.

## Check Status

```powershell
npx wrangler containers list
npx wrangler containers images list
```

Then open the `workers.dev` URL printed by Wrangler.
