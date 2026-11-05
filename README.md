# Supabase authentication API

Copy `.env.example` to `.env` and fill in your Supabase project URL and publishable/anon key. Install `pip install -r requirements.txt`, then run `uvicorn app:app --reload`. Swagger with bearer authorization is at `/docs`. Signup may require email confirmation before login depending on project settings.

| Method | Path | Bearer required |
|---|---|---|
| POST | /auth/signup, /auth/login | No |
| POST | /auth/logout | Yes |
| GET | /public/info | No |
| GET | /protected/profile, /protected/dashboard | Yes |

The backend uses the Supabase Python SDK to verify every bearer token and sign out the caller's session. Each request gets a fresh SDK client rather than sharing a mutable user session. Supabase logout revokes refresh sessions; an already-issued JWT may remain valid until expiry. Do not put a service role key in this app. [Swagger screenshot](swagger.png) shows the routes and authorization control.

Live Supabase verification on 2026-11-05 used a new temporary test account with email confirmation disabled: signup 201, login 200, missing token 401, tampered token 401, profile 200, dashboard 200, logout 204. Credentials and tokens were neither printed nor committed. Enable Email sign-in and new signups in your project; if email confirmation is enabled, confirm the account before login.
