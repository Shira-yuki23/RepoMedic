import asyncio
import json
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import app
from app.nebius import diagnose_with_nebius
from app.repository import RepositorySnapshot, limited_get, read_repository
from app.schemas import DiagnosisRequest

SHA = 'a' * 40
SETTINGS = Settings('test-key', 'nvidia/nemotron-3-super-120b-a12b', 'https://api.tokenfactory.us-central1.nebius.com/v1', 'demo-token')
REQUEST = DiagnosisRequest(repo_url='https://github.com/example/demo', bug_description='API returns the wrong value.', mode='live')
SNAPSHOT = RepositorySnapshot(SHA, {'app.py': 'def answer():\n    return 41\n'}, False)


def model_response(evidence=None):
    report = {'title': 'Check return value', 'summary': 'The return value may be incorrect.', 'steps': ['Write a regression test.'], 'evidence': evidence or []}
    return {'choices': [{'message': {'content': json.dumps(report)}}]}


def call_model(handler, settings=SETTINGS):
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await diagnose_with_nebius(client, settings, REQUEST, SNAPSHOT)
    return asyncio.run(run())


def test_valid_model_evidence_is_pinned_to_commit():
    def handler(request):
        payload = json.loads(request.content)
        assert request.headers['Authorization'] == 'Bearer test-key'
        assert '1: def answer()' in payload['messages'][1]['content']
        return httpx.Response(200, json=model_response([{'path': 'app.py', 'line': 2, 'explanation': 'Returns 41.'}]))
    result = call_model(handler)
    assert result.mode == 'live'
    assert result.evidence[0].url == f'https://github.com/example/demo/blob/{SHA}/app.py#L2'
    assert result.files_reviewed == ['app.py']


@pytest.mark.parametrize('path,line', [('invented.py', 1), ('app.py', 999)])
def test_model_cannot_cite_unreviewed_source(path, line):
    with pytest.raises(HTTPException) as error:
        call_model(lambda _: httpx.Response(200, json=model_response([{'path': path, 'line': line, 'explanation': 'Unverified.'}])))
    assert error.value.status_code == 502


def test_invalid_model_json_is_reported():
    with pytest.raises(HTTPException) as error:
        call_model(lambda _: httpx.Response(200, json={'choices': [{'message': {'content': 'not json'}}]}))
    assert error.value.status_code == 502


def test_model_authentication_failure_does_not_expose_key():
    with pytest.raises(HTTPException) as error:
        call_model(lambda _: httpx.Response(401, text='test-key'))
    assert error.value.status_code == 503
    assert 'test-key' not in error.value.detail


def test_credentials_cannot_be_sent_to_another_host():
    settings = Settings('test-key', 'model', 'https://example.com/v1', 'demo-token')
    with pytest.raises(HTTPException) as error:
        call_model(lambda _: pytest.fail('No HTTP request should occur'), settings)
    assert error.value.status_code == 503


def test_repository_retrieval_skips_dependencies_and_pins_source():
    seen = []
    def handler(request):
        seen.append(str(request.url))
        if request.url.host == 'raw.githubusercontent.com':
            assert f'/{SHA}/' in request.url.path
            return httpx.Response(200, text='def answer():\n    return 41\n')
        if '/git/trees/' in request.url.path:
            return httpx.Response(200, json={'tree': [
                {'path': 'app.py', 'type': 'blob', 'mode': '100644', 'size': 28},
                {'path': 'node_modules/dependency.js', 'type': 'blob', 'size': 10},
                {'path': '.env', 'type': 'blob', 'size': 10},
                {'path': 'large.py', 'type': 'blob', 'size': 9000},
            ]})
        if '/commits/' in request.url.path:
            return httpx.Response(200, json={'sha': SHA})
        return httpx.Response(200, json={'default_branch': 'main'})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await read_repository(client, REQUEST.repo_url, REQUEST.bug_description)
    result = asyncio.run(run())
    assert list(result.files) == ['app.py']
    assert len(seen) == 4


def test_repository_stream_enforces_size_limit():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b'x' * 20))) as client:
            await limited_get(client, 'https://api.github.com/example', 10)
    with pytest.raises(HTTPException) as error:
        asyncio.run(run())
    assert error.value.status_code == 413


def test_live_mode_requires_configuration(monkeypatch):
    monkeypatch.delenv('NEBIUS_API_KEY', raising=False)
    monkeypatch.delenv('REPOMEDIC_ACCESS_TOKEN', raising=False)
    response = TestClient(app).post('/api/diagnose', json=REQUEST.model_dump())
    assert response.status_code == 503


def test_live_mode_requires_demo_access_token(monkeypatch):
    monkeypatch.setenv('NEBIUS_API_KEY', 'test-key')
    monkeypatch.setenv('REPOMEDIC_ACCESS_TOKEN', 'demo-token')
    client = TestClient(app)
    assert client.get('/api/config').json()['live_available'] is True
    response = client.post('/api/diagnose', json=REQUEST.model_dump(), headers={'X-RepoMedic-Token': 'wrong'})
    assert response.status_code == 401
    assert 'test-key' not in client.get('/api/config').text


def test_production_static_frontend_is_served():
    response = TestClient(app).get('/')
    assert response.status_code == 200
    assert 'RepoMedic' in response.text
    assert TestClient(app).get('/api/health').status_code == 200
