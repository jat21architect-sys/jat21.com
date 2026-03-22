# Recovery Runbook

Procedures for recovering the Jeannote production deployment from partial or
complete failure. Use this when Railway, the database, or media storage is in
a degraded state.

---

## Environment variables — required for a working production deployment

All must be set in Railway → Service → Variables before deploying.

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | **Yes** | Django secret key — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DJANGO_SETTINGS_MODULE` | **Yes** | `config.settings.prod` |
| `ALLOWED_HOSTS` | **Yes** | Comma-separated, e.g. `jeannote.up.railway.app,yourdomain.com` |
| `CSRF_TRUSTED_ORIGINS` | **Yes** | Comma-separated with scheme, e.g. `https://yourdomain.com` |
| `DATABASE_URL` | **Yes** | Postgres connection string — provisioned automatically by Railway Postgres |
| `CLOUDINARY_CLOUD_NAME` | **Yes** | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | **Yes** | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | **Yes** | From Cloudinary dashboard |
| `EMAIL_BACKEND` | **Yes** | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | **Yes** | SMTP server hostname |
| `EMAIL_PORT` | **Yes** | `587` (TLS) |
| `EMAIL_USE_TLS` | **Yes** | `True` |
| `EMAIL_HOST_USER` | **Yes** | SMTP username |
| `EMAIL_HOST_PASSWORD` | **Yes** | SMTP password |
| `DEFAULT_FROM_EMAIL` | Recommended | From address for contact form emails |
| `CONTACT_EMAIL` | Recommended | Recipient for contact form notifications |
| `SENTRY_DSN` | Recommended | Sentry project DSN (see `docs/sentry-rollout.md`) |
| `SENTRY_ENVIRONMENT` | Recommended | `production` |

---

## Database

**Ownership:** Railway Postgres service attached to the jeannote project.

**Recovery assumptions:**
- Railway Postgres includes automatic daily backups (check Railway dashboard → Postgres service → Backups)
- The schema is fully reproducible from Django migrations — a blank database can be brought up to the current schema with `python manage.py migrate`
- Content (projects, site settings, about profile, etc.) is **not** in the git repo — it lives in the database only. If the database is lost without a backup, content must be re-entered via admin

**Backup a snapshot manually:**
```bash
# From Railway shell or a connected psql client:
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

**Restore from a dump:**
```bash
psql $DATABASE_URL < backup_YYYYMMDD_HHMMSS.sql
```

---

## Media files

**Storage:** Cloudinary (production). Django's `DEFAULT_FILE_STORAGE` is set to
`cloudinary_storage.storage.MediaCloudinaryStorage` in `config/settings/prod.py`.

**Recovery assumptions:**
- Cloudinary is the durable source of truth for all uploaded images
- Re-deploying Django does not affect Cloudinary assets — files survive Railway redeploys
- If a Cloudinary asset is deleted manually, it must be re-uploaded via the Django admin
- Local `media/` directory is only used in development (local filesystem) — not in production

**If Cloudinary credentials are lost:**
1. Log in to [cloudinary.com](https://cloudinary.com) and retrieve the cloud name, API key, and secret
2. Update the Railway env vars and redeploy

---

## Redeploy from scratch

Complete path from a blank Railway project to a working deployment:

```bash
# 1. Fork/clone the repo
git clone https://github.com/ksbk/jeannote.git
cd jeannote

# 2. In Railway: create a new project, add a Postgres service, connect the repo

# 3. Set all required env vars (see table above) in Railway → Variables

# 4. Railway will auto-deploy via Procfile:
#    web: python manage.py migrate --noinput && \
#         python manage.py collectstatic --noinput && \
#         gunicorn config.wsgi:application ...

# 5. After first deploy, create the admin user:
#    In Railway shell:
python manage.py createsuperuser

# 6. Log in to /admin/ and re-enter site content:
#    - SiteSettings (site name, tagline, contact info, social links)
#    - AboutProfile (headline, bio, portrait, CV)
#    - Projects (title, images, description, etc.)
#    - Services
```

---

## Verify health after a redeploy

```bash
# Set the production URL
BASE_URL=https://your-production-domain.com

# Full smoke check (requires Python; can run from local machine)
python scripts/smoke_check.py --base-url "$BASE_URL"

# Quick curl spot-check
curl -s -o /dev/null -w "home:    %{http_code}\n" "$BASE_URL/"
curl -s -o /dev/null -w "projects: %{http_code}\n" "$BASE_URL/projects/"
curl -s -o /dev/null -w "sitemap: %{http_code}\n" "$BASE_URL/sitemap.xml"

# Verify 404 page is branded (not Django default)
curl -s "$BASE_URL/does-not-exist/" | grep -q "Page not found" && echo "404 branded: OK" || echo "404 branded: MISSING"
```

---

## First actions in a real incident

1. Check Railway deployment log — is the process running? Did the Procfile command exit?
2. Check `python manage.py check --deploy` output (use `make check-deploy` locally)
3. Verify all required env vars are set — missing vars are the most common cause of startup failure
4. If the database is unreachable: check Railway Postgres service status and `DATABASE_URL`
5. If media is broken: check Cloudinary credentials and the `DEFAULT_FILE_STORAGE` setting
6. If pages 500: check Sentry for the event (if `SENTRY_DSN` is set)
7. Rollback: in Railway → Deployments, click the last known-good deploy and click **Redeploy**
