# RepoMedic

Repository triage for the Nebius × NVIDIA hackathon project. Submit a GitHub repository URL and a bug description to receive a structured **mock** investigation checklist.

## Milestone 1

- React/Vite frontend with validation, loading, error, and result states
- FastAPI backend with validated request/response models
- Keyword-based mock diagnosis provider
- MIT license and API tests

This version does not fetch repositories, analyze source code, or call an AI model. A syntactically valid URL does not guarantee that a repository exists or is public.

## Run locally

Prerequisites: Node.js 20.19+ or 22.12+, npm, Python 3.10+.

In terminal 1:

```sh
cd backend
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

In terminal 2:

```sh
cd frontend
npm ci
npm run dev
```

Open http://127.0.0.1:5173. API docs: http://127.0.0.1:8000/docs.
Vite forwards `/api` to FastAPI, so no cross-origin browser configuration is needed for local development.

## Verify

```sh
cd backend
python -m pytest
```

```sh
cd frontend
npm run build
```

## API

`GET /api/health` returns service status and mock mode.

`POST /api/diagnose` accepts:

```json
{"repo_url":"https://github.com/owner/repository","bug_description":"Clicking the submit button causes a network error."}
```

The response contains `mode`, `repo_url`, `title`, `summary`, `steps`, and `disclaimer`. Invalid input returns HTTP 422.

## Structure and architecture

```text
frontend/                 React UI and Vite development proxy
backend/app/main.py       HTTP endpoints
backend/app/schemas.py    Validated API contract
backend/app/providers.py Diagnosis provider boundary and mock implementation
backend/tests/           API regression tests
docs/architecture.md     Flow, boundaries, and next milestone
```

## Roadmap

1. Completed: input → validated API → mock checklist → report.
2. Next: implement a Nebius-hosted Nemotron provider behind `DiagnosisProvider`; keep credentials on the backend.
3. Later: bounded repository ingestion, grounded findings with file references, and patch suggestions with human review.

Production hosting is not configured. The frontend build requires an `/api` reverse proxy to FastAPI. Never put model API keys in frontend code.

## License

MIT. See [LICENSE](LICENSE).
