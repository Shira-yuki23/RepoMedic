# Architecture

## Current flow

React form → Vite `/api` proxy → FastAPI/Pydantic validation → MockDiagnosisProvider → typed report → React result panel.

The service is stateless. It stores no reports and makes no outbound requests. Keyword matches choose a checklist, not a root-cause diagnosis. Frontend output is rendered as text.

## Provider boundary

`DiagnosisProvider` defines `diagnose(DiagnosisRequest) -> DiagnosisResponse`. The route currently selects the mock implementation. A future Nebius/Nemotron implementation can preserve the API response contract while adding a real asynchronous inference path, timeouts, and provider error handling.

## Next milestone

- Verify Nebius model availability and Nemotron model identifier before implementing integration.
- Read credentials from server environment variables; keep secrets out of Git and browser bundles.
- Add bounded repository retrieval with size/time limits and explicit handling of unavailable repositories.
- Treat repository content as untrusted input; do not execute submitted code.
- Require evidence with file/line references and clearly distinguish hypotheses from confirmed findings.
- Add mocked provider contract tests before live model smoke tests.

Repository scanning, automated patches, authentication, persistence, rate limiting, and deployment are future scope.
