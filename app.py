import os
import requests
import httpx
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.responses import JSONResponse, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import ClientOptions, create_client
from supabase_auth.errors import AuthApiError

load_dotenv()
app = FastAPI(title="Supabase auth exercise")
security = HTTPBearer(auto_error=False)

class Provider:
    def client(self):
        url = os.getenv("SUPABASE_URL", "").rstrip("/")
        key = os.getenv("SUPABASE_KEY", "")
        if not url or not key: raise RuntimeError("Supabase configuration missing")
        return create_client(url, key, options=ClientOptions(persist_session=False, auto_refresh_token=False))
    def signup(self, data):
        result = self.client().auth.sign_up(data)
        return result.user.model_dump(mode="json") if result.user else {}
    def login(self, data):
        session = self.client().auth.sign_in_with_password(data).session
        if not session: raise RuntimeError("No session returned")
        return {"access_token":session.access_token, "refresh_token":session.refresh_token}
    def user(self, token):
        try:
            result = self.client().auth.get_user(token)
            return result.user.model_dump(mode="json") if result and result.user else None
        except AuthApiError: return None
    def logout(self, token):
        self.client().auth.admin.sign_out(token)

provider = Provider()

@app.exception_handler(RuntimeError)
@app.exception_handler(requests.RequestException)
@app.exception_handler(httpx.RequestError)
async def upstream_error(request, exc): return JSONResponse({"error": "Authentication provider unavailable"}, status_code=503)

@app.exception_handler(HTTPException)
async def auth_error(request, exc): return JSONResponse({"error": exc.detail}, status_code=exc.status_code)

async def credentials(request):
    try: data = await request.json()
    except ValueError: return None
    if not isinstance(data, dict) or not isinstance(data.get("email"), str) or not data["email"].strip() or not isinstance(data.get("password"), str) or not data["password"]: return None
    return {"email": data["email"], "password": data["password"]}

def verified(auth: HTTPAuthorizationCredentials = Security(security)):
    if auth is None: raise HTTPException(401, "Access token required")
    user = provider.user(auth.credentials)
    if user is None: raise HTTPException(401, "Invalid or expired token")
    return {"user": user, "token": auth.credentials}

@app.get("/public/info")
def public(): return {"message": "Welcome stranger! This info is public."}

credentials_schema={"requestBody":{"required":True,"content":{"application/json":{"schema":{"type":"object","properties":{"email":{"type":"string","format":"email"},"password":{"type":"string","format":"password"}},"required":["email","password"]}}}}}

@app.post("/auth/signup", status_code=201, openapi_extra=credentials_schema)
async def signup(request: Request):
    body = await credentials(request)
    if not body: return JSONResponse({"error":"Email and password required"}, status_code=400)
    try: return provider.signup(body)
    except AuthApiError: return JSONResponse({"error":"Signup failed"}, status_code=400)

@app.post("/auth/login", openapi_extra=credentials_schema)
async def login(request: Request):
    body = await credentials(request)
    if not body: return JSONResponse({"error":"Email and password required"}, status_code=400)
    try: return provider.login(body)
    except AuthApiError: return JSONResponse({"error":"Invalid login credentials"}, status_code=401)

@app.get("/protected/profile")
def profile(session=Depends(verified)):
    user=session["user"]; return {k:user.get(k) for k in ("id", "email", "created_at")}

@app.get("/protected/dashboard")
def dashboard(session=Depends(verified)): return {"message":"Authenticated", "user_id":session["user"]["id"]}

@app.post("/auth/logout", status_code=204)
def logout(session=Depends(verified)):
    try: provider.logout(session["token"])
    except AuthApiError: return JSONResponse({"error":"Logout failed"}, status_code=502)
    return Response(status_code=204)
