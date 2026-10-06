# Deploy RepoMedic

## Status

Live retrieval and Nebius/Nemotron integration are implemented. Account creation, server credentials, a live model smoke test, and a public deployment must still be completed. Mock mode works without credentials.

## Accounts and secrets

1. Create a [Nebius Token Factory account](https://tokenfactory.nebius.com/). Complete its signup and any account terms yourself. Obtain hackathon credits if provided; inference usage can incur charges.
2. Create an API key in Token Factory. Keep it out of chat, Git, and frontend code.
3. Confirm the model `nvidia/nemotron-3-super-120b-a12b` is available to your account. Set `NEBIUS_MODEL` to an available Nemotron model if needed. The default endpoint/model are taken from [Nebius's official example](https://nebius.com/services/token-factory/nemotron).
4. Create a [Render account](https://dashboard.render.com/). Complete account terms yourself.

## Render deployment

The root `render.yaml` defines one Docker web service on the free plan. See [Render Blueprints](https://render.com/docs/blueprint-spec) and [Docker deployment](https://render.com/docs/docker).

1. In Render, create a Blueprint from `https://github.com/Shira-yuki23/RepoMedic` on `main`.
2. Set `NEBIUS_API_KEY` using Render's environment settings. Do not type it into a public file.
3. Render generates `REPOMEDIC_ACCESS_TOKEN`. Retrieve it from the service environment settings and share only with authorized demo users. This is a separate access token, not your Nebius key.
4. Deploy and wait for the health check. Open the assigned HTTPS service URL.
5. Test mock mode first, then select live mode and enter the demo access token.
6. Use a small public repository and a specific bug report. Verify the report references real source lines and the expected commit.

The hosting plan is specified as free. Review any provider billing prompts before proceeding. Cold starts and provider limits may affect a free demo deployment. The token and two concurrent analysis slots protect access and bound concurrency; this MVP has no durable per-user quotas.

## Local live configuration

Copy `backend/.env.example` to `backend/.env`, set `NEBIUS_API_KEY` and a separate `REPOMEDIC_ACCESS_TOKEN`, and restart the backend. Configuration is read at startup; do not share this file.

Python 3.11+ is required. Install backend requirements, build the frontend, then run:

```sh
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. FastAPI serves the frontend and API together. For separate Vite development, keep the existing port-5173 proxy workflow.

## Container

```sh
docker build -t repomedic .
docker run --rm -p 8000:8000 --env-file backend/.env repomedic
```

The container excludes environment files and runs as a non-root user. Model inference is remote; no GPU is required for the web service.

## Retrieval and output limits

Live mode fetches only public GitHub content, using a commit-pinned source snapshot. It samples up to 12 UTF-8 files, at most 8 KB per file and 60 KB in total, selected by extension and bug-related path keywords. Dependencies, hidden directories, symlinks, lock files, and oversized files are skipped. This is a bounded sample, not a complete codebase audit.

The model receives the bug report and selected source excerpts. The backend validates JSON and rejects citations outside the reviewed files and line ranges. That validation confirms citation existence, not the truth of the model's explanation. No code is executed and no patches are applied.

## Verification before marking deployment complete

- Frontend production build and backend tests pass.
- Docker image builds successfully on the deployment host.
- Public `/api/health`, homepage, and mock flow respond successfully.
- Correct demo token permits a live report; missing/incorrect token returns 401.
- A real Nebius inference request returns a report with appropriate citations.
- Keys and demo access tokens are absent from Git and the browser bundle.
