from fastapi.testclient import TestClient
from app import app, provider

def test_protected_route_checks_bearer(monkeypatch):
    monkeypatch.setattr(provider, "user", lambda token: {"id":"1", "email":"a@example.com"} if token == "valid" else None)
    c = TestClient(app)
    assert c.get("/public/info").status_code == 200
    assert c.get("/protected/profile").status_code == 401
    assert c.get("/protected/profile", headers={"Authorization":"Bearer invalid"}).status_code == 401
    assert c.get("/protected/profile", headers={"Authorization":"Bearer valid"}).json()["id"] == "1"
    assert c.post("/auth/login", json={}).status_code == 400
