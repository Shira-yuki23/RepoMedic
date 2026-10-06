import asyncio
import os
import secrets
from pathlib import Path
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles
from .config import Settings
from .nebius import diagnose_with_nebius
from .repository import read_repository
from .providers import MockDiagnosisProvider
from .schemas import DiagnosisRequest, DiagnosisResponse

app = FastAPI(title='RepoMedic API', version='0.2.0')
provider = MockDiagnosisProvider()
live_slots = asyncio.Semaphore(2)


@app.get('/api/health')
def health():
    return {'status': 'ok', 'mode': 'mock'}


@app.get('/api/config')
def configuration():
    settings = Settings.from_env()
    return {'live_available': settings.live_available, 'model': settings.model, 'access_token_required': True}


@app.post('/api/diagnose', response_model=DiagnosisResponse)
async def diagnose(request: DiagnosisRequest, x_repomedic_token: str = Header(default='')):
    if request.mode == 'mock':
        return provider.diagnose(request)
    settings = Settings.from_env()
    if not settings.live_available:
        raise HTTPException(503, 'Live diagnosis needs server-side Nebius and demo access-token configuration.')
    if not secrets.compare_digest(x_repomedic_token, settings.access_token):
        raise HTTPException(401, 'Enter the correct demo access token to use live diagnosis.')
    try:
        await asyncio.wait_for(live_slots.acquire(), timeout=1)
    except TimeoutError:
        raise HTTPException(429, 'Both live analysis slots are busy. Please try again shortly.') from None
    try:
        async with asyncio.timeout(100):
            async with httpx.AsyncClient(timeout=30, follow_redirects=False, headers={'User-Agent': 'RepoMedic/0.2', 'Accept': 'application/vnd.github+json'}) as github:
                snapshot = await read_repository(github, request.repo_url, request.bug_description)
            async with httpx.AsyncClient(timeout=70, follow_redirects=False) as nebius:
                return await diagnose_with_nebius(nebius, settings, request, snapshot)
    except (httpx.TimeoutException, TimeoutError):
        raise HTTPException(504, 'Analysis timed out. Try a smaller repository or retry shortly.') from None
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        raise HTTPException(502, 'An upstream service returned an unavailable or invalid response.') from None
    finally:
        live_slots.release()


static_directory = Path(os.getenv('REPOMEDIC_STATIC_DIR', Path(__file__).resolve().parents[2] / 'frontend' / 'dist'))
if static_directory.is_dir():
    app.mount('/', StaticFiles(directory=static_directory, html=True), name='frontend')
