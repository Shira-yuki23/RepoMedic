# Architecture

Mock: React form → FastAPI/Pydantic validation → MockDiagnosisProvider → labeled checklist.

Live: React form and demo token → FastAPI access check and concurrency gate → GitHub metadata/commit/tree → bounded source sample → Nebius Token Factory/Nemotron → JSON schema and citation validation → report with source links.

`config.py` loads backend environment settings. `repository.py` fetches only fixed GitHub API/raw origins, without following redirects, and pins excerpts to a commit. `nebius.py` calls an allowlisted HTTPS Nebius endpoint and verifies returned file/line references. `main.py` reports upstream failures and serves the production frontend after API routes.

The service is stateless. It does not store reports, execute repository code, or apply patches. Source and bug reports are treated as untrusted prompt data. Prompts cannot guarantee immunity to injection; returned claims require human review even when citations exist.

A Docker image builds Vite assets and runs FastAPI as a non-root user. Render can deploy the root Blueprint. Live inference requires both a server-side Nebius key and a separate demo token; public mock mode requires neither. The current two-slot limit bounds concurrency, not total spending or per-user quotas.

Next validation: real Nebius account/model smoke test, deployed image build, public HTTPS checks, and live end-to-end test. Production evolution: durable quotas, user authentication, richer retrieval, and evaluation against known bugs.
