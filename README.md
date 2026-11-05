# Supabase authentication API

Copy `.env.example` to `.env` and fill in your Supabase project URL and publishable/anon key. Install `pip install -r requirements.txt`, then run `uvicorn app:app --reload`. Swagger with bearer authorization is at `/docs`. Signup may require email confirmation before login depending on project settings.

| Method | Path | Bearer required |
|---|---|---|
| POST | /auth/signup, /auth/login | No |
| POST | /auth/logout | Yes |
| GET | /public/info | No |
| GET | /protected/profile, /protected/dashboard | Yes |

The backend asks Supabase Auth to verify every bearer token, and sends logout using the caller's token. Supabase logout revokes refresh sessions; an already-issued JWT may remain valid until expiry. Do not put a service role key in this app. [Swagger screenshot](swagger.png) shows the routes and authorization control. Tests use a fake provider; a real Supabase project remains necessary to verify the complete authentication flow.
