# RepoMedic

Repository triage for the Nebius × NVIDIA hackathon project. React/Vite + FastAPI, with a mock demo and a live Nebius/Nemotron analysis path.

## Features

- Repository URL and bug description form with mock/live modes
- Bounded public GitHub source retrieval, pinned to a commit
- Nebius Token Factory inference with configurable Nemotron model
- Structured hypotheses, investigation steps, and validated source citations
- Server-side secrets, demo access token, timeouts, and two concurrent live slots
- Same-origin production hosting with Docker and a Render Blueprint
- MIT license and API/provider/retrieval tests

Public demo: https://repomedic-65eq.onrender.com (Render free plan). Live integration is implemented but needs a configured Nebius account/key and a real inference smoke test. Mock mode works without accounts.

## Local setup

Prerequisites: Node.js 20.19+ or 22.12+, npm, Python 3.11+.

```sh
cd frontend
npm ci
npm run build
```

```sh
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. FastAPI serves the built UI and API together. API docs: http://127.0.0.1:8000/docs.

For frontend development, run `npm run dev` in `frontend` and use http://127.0.0.1:5173. Vite proxies `/api` to port 8000. In restricted environments where the Vite config bundler cannot read ancestor directories, build with `npm run build -- --configLoader native`.

## Enable live mode

Copy `backend/.env.example` to `backend/.env`. Set `NEBIUS_API_KEY`, an available `NEBIUS_MODEL`, and a separate `REPOMEDIC_ACCESS_TOKEN`. Restart the backend. Never commit real secrets or put the Nebius key in the browser. Live mode requires the demo access token and sends your bug report plus selected public source excerpts to Nebius.

## API

- `GET /api/health`: service health
- `GET /api/config`: live availability and model name, without credentials
- `POST /api/diagnose`: structured mock or live report

```json
{"repo_url":"https://github.com/owner/repository","bug_description":"The API returns an incorrect value.","mode":"mock"}
```

For `mode: live`, provide `X-RepoMedic-Token`. Invalid input returns 422; incorrect token 401; missing server configuration 503; upstream timeout 504. Model errors are reported without silently substituting a mock report.

## Verification

```sh
cd backend
python -m pytest -q
```

```sh
cd frontend
npm run build
```

Tests cover mock flow, input validation, bounded retrieval, pinned evidence, rejected invented citations, provider errors, access control, and static frontend hosting. Provider tests use mocked HTTP responses; they do not establish real account/model availability.

## Deployment and architecture

See [deployment guide](docs/deployment.md) for account setup, credentials, Render, Docker, limits, and remaining verification. See [architecture](docs/architecture.md) for the request flow.

Live mode reviews a bounded source sample rather than the entire repository. Suggestions are hypotheses. Code and tests are not executed; patches are not applied.

## License

MIT. See [LICENSE](LICENSE).
