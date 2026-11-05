from fastapi.testclient import TestClient
from app import app, provider

def test_logout_verifies_and_passes_the_callers_token(monkeypatch):
    seen=[]
    monkeypatch.setattr(provider,'user',lambda token: {'id':'user-1'} if token=='valid' else None)
    monkeypatch.setattr(provider,'logout',lambda token: seen.append(token))
    client=TestClient(app)
    assert client.post('/auth/logout').status_code==401
    assert client.post('/auth/logout',headers={'Authorization':'Bearer invalid'}).status_code==401
    assert client.post('/auth/logout',headers={'Authorization':'Bearer valid'}).status_code==204
    assert seen==['valid']
