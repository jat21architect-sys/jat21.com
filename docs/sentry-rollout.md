# Sentry Rollout Checklist

Code support is complete and on `main`. Sentry is not active until `SENTRY_DSN`
is set in Railway. Follow this checklist when you have dashboard access.

---

## 1 — Get the DSN from Sentry

1. Log in to [sentry.io](https://sentry.io)
2. Open the project (or create one if it does not exist — use platform **Django**)
3. Go to **Settings → Projects → [project] → Client Keys (DSN)**
4. Copy the DSN. It looks like:
   `https://abc123def456@o123456.ingest.sentry.io/789012`

---

## 2 — Set the env var in Railway

1. Open the Railway project dashboard
2. Go to the service → **Variables**
3. Add the following (at minimum):

   | Variable           | Value                           |
   |--------------------|---------------------------------|
   | `SENTRY_DSN`       | the DSN from step 1             |
   | `SENTRY_ENVIRONMENT` | `production`                  |

4. Optional but recommended:
   - `SENTRY_RELEASE` — set to the current git SHA
     (`git rev-parse --short HEAD`) for stack trace linkage
   - `SENTRY_TRACES_SAMPLE_RATE` — `0.1` to collect 10% of transactions
     (leave at `0.0` to disable performance tracing entirely)

---

## 3 — Redeploy

Railway picks up new env vars automatically on the next deploy trigger.

- In the Railway UI: **Deploy → Trigger redeploy** (or push any commit)
- The deploy chain is: `python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn config.wsgi:application ...`
- Wait for the deployment health check to go green before proceeding

---

## 4 — Trigger a safe verification event

Option A — from a browser (no code needed):
1. Visit `https://your-production-domain.com/this-path-does-not-exist-sentry-test/`
2. This triggers a genuine 404 — Sentry captures it as an event with request context

Option B — from Railway shell or local machine (more explicit):
```bash
# Set your production URL
BASE_URL=https://your-production-domain.com

# Hit a real 404 — Sentry should capture it
curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/sentry-test-probe/"
# Expected: 404
```

Do **not** use Sentry's built-in "Send Test Event" button for initial verification —
it bypasses Django middleware and does not confirm the DjangoIntegration is wired.

---

## 5 — Confirm the event appears in Sentry

1. Open Sentry → **Issues** (or **Discover** for events)
2. Filter by project and environment `production`
3. Look for the 404 event from the path you just requested
4. Confirm the event includes:
   - URL and HTTP method
   - Django version and Python version in the "Platform" section
   - No PII in request data (unless you opted in via `SENTRY_SEND_DEFAULT_PII`)

If the event appears within ~30 seconds, Sentry is live.

---

## Status

| Step | Status |
|------|--------|
| Code merged to `main` | ✅ Done |
| `SENTRY_DSN` set in Railway | ⏳ Pending external access |
| Redeployed | ⏳ Pending external access |
| Verification event confirmed | ⏳ Pending external access |
