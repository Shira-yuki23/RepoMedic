from typing import Protocol
from .schemas import DiagnosisRequest, DiagnosisResponse


class DiagnosisProvider(Protocol):
    def diagnose(self, request: DiagnosisRequest) -> DiagnosisResponse: ...


class MockDiagnosisProvider:
    def diagnose(self, request: DiagnosisRequest) -> DiagnosisResponse:
        symptom = request.bug_description.lower()
        if any(word in symptom for word in ('fetch', 'api', 'network', 'cors')):
            focus = 'Request and response handling'
            investigation = 'Inspect the failing request, status code, response body, and API configuration.'
        elif any(word in symptom for word in ('render', 'button', 'screen', 'react', 'ui')):
            focus = 'Interface state and event handling'
            investigation = 'Trace the event handler and state transitions; inspect browser console errors.'
        else:
            focus = 'Reproduction and execution path'
            investigation = 'Trace the smallest failing execution path and record its inputs and error output.'
        return DiagnosisResponse(
            repo_url=request.repo_url,
            title=focus,
            summary='This demo selected an investigation checklist from keywords in your bug report. It has not inspected repository code or established a root cause.',
            steps=[
                'Reproduce the reported behavior with the smallest possible example; record expected and actual results.',
                investigation,
                'Add a regression test that fails with the reproduced symptom before making a fix.',
                'Apply a focused fix, then run the regression test and the relevant project checks.',
            ],
            disclaimer='Mock output only. Suggestions are unverified. Nebius and Nemotron integration is planned for a later milestone.',
        )
