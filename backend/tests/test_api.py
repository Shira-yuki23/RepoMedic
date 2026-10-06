from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_mock_diagnosis():
    response = client.post('/api/diagnose', json={'repo_url': 'https://github.com/example/demo/', 'bug_description': 'API fetch fails with a network error.'})
    assert response.status_code == 200
    assert response.json()['mode'] == 'mock'
    assert response.json()['repo_url'] == 'https://github.com/example/demo'
    assert response.json()['title'] == 'Request and response handling'
    assert len(response.json()['steps']) == 4


def test_reject_non_repository_url():
    assert client.post('/api/diagnose', json={'repo_url': 'https://example.com/demo', 'bug_description': 'The button stops responding.'}).status_code == 422


def test_reject_blank_description():
    assert client.post('/api/diagnose', json={'repo_url': 'https://github.com/example/demo', 'bug_description': ' ' * 20}).status_code == 422


def test_health():
    assert client.get('/api/health').json() == {'status': 'ok', 'mode': 'mock'}
