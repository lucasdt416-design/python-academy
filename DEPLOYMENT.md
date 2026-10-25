# Python Academy deployment

Deployed on 2026-10-24.

## Running services

- App: https://python-academy-dji8.onrender.com/
- API: https://python-academy-api.onrender.com
- Render Blueprint: https://dashboard.render.com/blueprint/exs-dbeggu1srm7s73c301cg
- Frontend service: srv-dbeglavb9u1s739lickg
- API service: srv-dbegkrfb9u1s739lh63g
- PostgreSQL: dpg-dbegk87b9u1s739lfkfg-a
- Region: Oregon
- Database compute: Basic-256mb; provisioned storage: 15 GB, autoscaling off.
- Compute baseline: USD 20/month for two Starter web services and Basic-256mb PostgreSQL, plus database storage, workspace subscription, taxes and metered usage.

## Verified

The frontend and API have live deployments. The app homepage, proxied /health, /api/lessons and Python worker return HTTP 200. Anonymous /api/me returns 401. PostgreSQL contains users, invitations, events and attempts tables. Local validation passed 15 backend tests, 8 Chromium tests and a production build. The initial Render frontend build omitted development dependencies; the build now explicitly runs npm ci --include=dev.

## Google sign-in: configured and verified

The owner created the Google OAuth Web application client and entered its credentials directly in Render. The API redeployed successfully. The production OAuth flow redirected to Google with state and nonce, completed Google verification and consent, returned to the app, and created one persistent account with a signed_in audit event. Parent enrollment is still pending the owner's date of birth. No client secret is stored in this repository.

The following steps document configuration for future maintenance:

1. Open https://console.cloud.google.com/auth/overview and select or create the application's project.
2. Configure Google Auth Platform branding as Python Academy, using the owner's support email. For initial testing, use an External audience in Testing and add the intended parent and learner test accounts.
3. Under Clients, create a Web application client named Python Academy.
4. Register the exact authorized redirect URI:
   https://python-academy-dji8.onrender.com/auth/google/callback
5. If Google asks for an authorized JavaScript origin, use:
   https://python-academy-dji8.onrender.com
6. Store GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET directly in the API service's Render Environment settings. Do not put the secret in chat, source control, screenshots or this file.
7. APP_ORIGIN and API_ORIGIN are already set on the API service to https://python-academy-dji8.onrender.com. Preserve the generated SESSION_SECRET and DATABASE_URL.
8. Save and deploy the API environment changes, then verify a real Google sign-in, parent registration, student invitation acceptance, practice history and logout with test accounts.

The application requests only openid, email and profile. Date of birth is self-declared in the app. Browser practice checks match output and do not certify conceptual understanding. Full WCAG 2.2 conformance and broader-release readiness are not certified.

## Database migrations

The API applies Alembic migrations itself when it starts (`backend/app/migrate.py`); no Render setting or extra command is needed.

- The first deploy with migrations finds the original four tables without migration history, checks their columns match the baseline, records them as migration 0001, then applies the later migrations. No existing row is changed. If the tables do not match, startup stops without changing anything, and Render keeps the previous version running.
- Migrations only add tables or nullable columns, so the previous version keeps working during a zero-downtime deploy.
- To confirm a deploy, open the API service's **Logs** in Render and look for `Database schema is at migration 0003` (or the latest number), then check `/health`.

## Rate limits and security headers

No Render settings are needed for either.

- **Rate limits** (`backend/app/limits.py`): counted in the API's memory, so they reset whenever the API restarts or redeploys. They assume one API instance. If the API is ever scaled to more than one instance, move the counters to the database first. A refused request gets HTTP 429 with a `Retry-After` header. The API log shows only `Rate limited: rule=<name> scope=user|ip`: no code, user ID or address.
- **Visitor address:** for signed-out limits and sign-in, the API uses the rightmost public address in `X-Forwarded-For`. Render's proxy adds the visitor's address, and the Next.js proxy passes it on unchanged. Handoff 06 has the live check that confirms this.
- **Headers** (`frontend/next.config.mjs` for pages, `backend/app/main.py` for the API): HSTS, `nosniff`, `no-referrer`, and framing blocked (`X-Frame-Options: DENY` and `frame-ancestors 'none'`). The page Content-Security-Policy is in Report-Only mode. Handoff 06 section 4 has the exact switch to enforce mode.
