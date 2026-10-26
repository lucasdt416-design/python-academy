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
- To confirm a deploy, open the API service's **Logs** in Render and look for `Database schema is at migration 0006` (or the latest number), then check `/health`.

## Rate limits and security headers

One API setting is needed, `CLIENT_IP_HEADER` (below). It is in `render.yaml`, so a rebuild from the Blueprint keeps it.

- **Rate limits** (`backend/app/limits.py`): counted in the API's memory, so they reset whenever the API restarts or redeploys. They assume one API instance. If the API is ever scaled to more than one instance, move the counters to the database first. A refused request gets HTTP 429 with a `Retry-After` header. The API log shows only `Rate limited: rule=<name> scope=user|ip`: no code, user ID or address.
- **Visitor address:** signed-out limits and sign-in are counted per address only when the API service has **one** trusted source set:
  - `CLIENT_IP_HEADER`: a header the edge sets and overwrites. **Production uses `CLIENT_IP_HEADER=cf-connecting-ip`**, set in `render.yaml`. The live checks on 2026-10-25 (handoff 06 section 13.7) showed Cloudflare, in front of Render, sends it on every request and refuses any request where the caller tries to set it (403, `error code: 1000`).
  - `TRUSTED_PROXY_HOPS`: how many `X-Forwarded-For` entries our own proxies add on the right. Not used in production.

  **Without either setting, all signed-out visitors share one counter**: 60 preview checks a minute and 60 sign-ins per 10 minutes across the whole site. That is safe, because nothing a caller sends can change it, but a few busy visitors would limit everyone. If the API is ever moved off Render or Cloudflare, check the header again (handoff 06 section 13.5) before keeping it.
- **Diagnostic:** off in production since 2026-10-25. `RATE_LIMIT_DIAGNOSTIC=1` on the API service logs, for each signed-out limited request, the number of `X-Forwarded-For` entries, the names of the forwarding headers present, the source used, and an 8-character keyed hash of the chosen address. It never logs an address, user ID, code or message text. The key changes on every restart, so hashes only compare within one deploy. Remove the variable when done.
- **Headers** (`frontend/next.config.mjs` for pages, `backend/app/main.py` for the API): HSTS, `nosniff`, `no-referrer`, and framing blocked (`X-Frame-Options: DENY` and `frame-ancestors 'none'`).
- **Page Content-Security-Policy** (`frontend/proxy.ts`, `frontend/csp.mjs`): a new random nonce for every page request, so only scripts the server added can run (backlog SEC-09). Because of the nonce, every page is rendered per request and sent with `Cache-Control: no-store`. It is in Report-Only mode; handoff 08 section 5 has the one-line switch to enforce mode. The Python worker keeps its own enforced policy. No Render settings are needed.

## Sign-in sessions

No Render settings are needed. Since stage 7 (backlog SEC-03, handoff 07):

- The session cookie, signed with `SESSION_SECRET`, holds only a random session ID. The `sessions` table (migration 0006) holds which user it belongs to, when it started, when it was last used and when it expires. The table stores a SHA-256 digest of the ID, not the ID itself.
- **Logout deletes the row**, so the old cookie stops working at once, even if someone copied it.
- A session ends **7 days** after sign-in however much it is used, or after **24 hours** without a request. Both are constants in `backend/app/sessions.py`.
- Deleting a user deletes their sessions (database cascade), and a session whose user is missing is refused.
- Expired rows are deleted at the next sign-in by anyone; no scheduled job is needed.
- Nothing about sessions is logged: no session ID, cookie, email or user ID.
- **Changing `SESSION_SECRET` signs everyone out**, as before. Deleting all rows (`DELETE FROM sessions`) also signs everyone out, without changing the secret.
