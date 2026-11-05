from fastapi.testclient import TestClient
from types import SimpleNamespace
import app as module

def test_uses_supabase_sdk_for_login_and_token_verification(monkeypatch):
    seen=[]
    class Auth:
        def sign_in_with_password(self, data):
            seen.append(('login',data['email']))
            return SimpleNamespace(session=SimpleNamespace(access_token='access',refresh_token='refresh'))
        def get_user(self, jwt):
            seen.append(('verify',jwt)); return SimpleNamespace(user=SimpleNamespace(model_dump=lambda mode: {'id':'42','email':'a@example.com'}))
    monkeypatch.setattr(module.provider,'client',lambda: SimpleNamespace(auth=Auth()))
    client=TestClient(module.app)
    assert client.post('/auth/login',json={'email':'a@example.com','password':'secret'}).json()['access_token']=='access'
    assert client.get('/protected/profile',headers={'Authorization':'Bearer access'}).json()['id']=='42'
    assert seen==[('login','a@example.com'),('verify','access')]
