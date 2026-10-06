from fastapi import FastAPI
from .providers import MockDiagnosisProvider
from .schemas import DiagnosisRequest, DiagnosisResponse

app = FastAPI(title='RepoMedic API', version='0.1.0')
provider = MockDiagnosisProvider()


@app.get('/api/health')
def health():
    return {'status': 'ok', 'mode': 'mock'}


@app.post('/api/diagnose', response_model=DiagnosisResponse)
def diagnose(request: DiagnosisRequest):
    return provider.diagnose(request)
