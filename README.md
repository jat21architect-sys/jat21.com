# Jeannot Tsirenge — Architecture Portfolio

A professional, content-driven portfolio platform built with Django.

---

## Stack

| Layer | Technology |
| --- | --- |
| Framework | Django 5.2 LTS |
| Language | Python 3.13 |
| Database | SQLite (dev) · PostgreSQL (prod) |
| Images | Pillow |
| Config | django-environ |
| Static files | whitenoise |
| Dependency management | [uv](https://docs.astral.sh/uv/) (pyproject.toml + uv.lock) |
| Linting / formatting | [Ruff](https://docs.astral.sh/ruff/) |
| Type checking | mypy + django-stubs |
| Testing | pytest + pytest-django + pytest-cov |
| CI | GitHub Actions |
| Git hooks | pre-commit |

---

## Local setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (`brew install uv` or see docs)

### 1. Clone and install

```bash
git clone <repo-url>
cd jeannote

# Install all dependencies (runtime + dev) into an isolated virtualenv
uv sync --group dev
```

### 2. Configure environment

```bash
cp .env.example .env
```

Open `.env` and set at minimum:

```dotenv
SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 3. Database

```bash
uv run python manage.py migrate
```

### 4. Create an admin user

```bash
uv run python manage.py createsuperuser
```

Enter your chosen username, email, and a strong password at the prompts.
There are no default credentials anywhere in this codebase.

### 5. Seed demo content (optional)

```bash
uv run python manage.py seed_demo
```

This populates demo site settings, an about profile, services, and placeholder
projects so the site renders immediately. Safe to run multiple times
(uses `get_or_create`). Does not create any user accounts.

### 6. Start the dev server

```bash
uv run python manage.py runserver
# or: make run
```

- Site: **<http://127.0.0.1:8000>**
- Admin: **<http://127.0.0.1:8000/admin>**

---

## Run locally with Docker

An alternative to the `uv` setup above. Useful for reproducible local start-up
across macOS and Windows without installing Python or uv on the host.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS / Windows)
  or Docker Engine + Compose plugin (Linux)

### 1. Copy the env file — **required before first run**

```bash
cp .env.example .env
```

Then open `.env` and set `SECRET_KEY`. Everything else works as-is for local dev.
`docker compose up` will fail immediately if `.env` does not exist.

### 2. Build and start

```bash
docker compose up --build
# or: make docker-up
```

The container runs `python manage.py migrate --noinput` before the dev server
starts, so the database is always up to date on each run.

- Site: **<http://localhost:8000>**
- Admin: **<http://localhost:8000/admin>**

### 3. Stop

```bash
docker compose down
# or: make docker-down
```

### 4. Useful one-off commands

```bash
# Open a shell inside the running container
docker compose exec web sh

# Run migrations manually (also runs automatically on `up`)
docker compose exec web python manage.py migrate

# Create an admin user
docker compose exec web python manage.py createsuperuser

# Seed demo content
docker compose exec web python manage.py seed_demo

# Run the test suite
docker compose exec web pytest
# or: make docker-test

# Run a single test file
docker compose exec web pytest tests/projects/test_views.py
```

### Notes

- The repo is bind-mounted into the container at `/app`. Code changes on the
  host are reflected immediately — Django's auto-reloader works as normal.
- The SQLite database (`db.sqlite3`) is also on the bind mount, so data
  persists between `docker compose down / up` cycles.
- The virtualenv lives at `/opt/venv` inside the image, outside the bind
  mount, so it is never shadowed when you start the container.
- This setup uses `config.settings.dev` (the default). It is **not** wired
  to Railway or any production config.
- **Production is not served from this Dockerfile.** Railway builds directly
  from `Procfile` + `railway.toml` via nixpacks — the `Dockerfile` and
  `compose.yml` are never used in that environment.
- If you prefer the `uv` workflow, see the [Local setup](#local-setup) section
  above. Both approaches are fully supported.

---

## Dependency management

| File | Role | Edit by hand? |
| --- | --- | --- |
| `pyproject.toml` | Authoring source — declares all runtime and dev dependencies | **Yes** |
| `uv.lock` | Full locked dependency graph for reproducible installs | No |
| `requirements.txt` | Generated export for Railway/nixpacks deployment | **No** — run `make reqs` |

Workflow when adding or changing a dependency:

```bash
# 1. Edit pyproject.toml (add/remove from [project].dependencies or [dependency-groups].dev)
# 2. Sync the lockfile and virtualenv
uv sync --group dev
# 3. Regenerate the deployment export
make reqs
# 4. Commit all three files together
git add pyproject.toml uv.lock requirements.txt
```

CI enforces that `requirements.txt` matches the declared dependencies (`make check-reqs`).
If you see a CI failure on that step, run `make reqs` and commit the result.

---

## Settings structure

```text
config/settings/
├── base.py     # Shared settings for all environments
├── dev.py      # Development overrides (DEBUG=True, console email)
└── prod.py     # Production hardening (HSTS, SSL redirect, secure cookies)
```

`manage.py` defaults to `config.settings.dev`. Set `DJANGO_SETTINGS_MODULE`
in your environment or deployment config to switch to `config.settings.prod`.

---

## Code quality

### Lint and format

```bash
uv run ruff check .          # lint
uv run ruff check . --fix    # lint with auto-fix
uv run ruff format .         # format
```

### Type checking

```bash
uv run mypy .
```

### One-command health gate

```bash
make health
```

This runs the standard repo guardrails in one pass:

- `ruff`
- `mypy`
- `pytest`
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `make check-reqs`

### Tests

Tests live in `tests/` organised by domain, mirroring the `apps/` layout:

```text
tests/
  conftest.py          # shared fixtures (site_settings, project, service)
  core/
    test_admin.py      # singleton admin guardrails
    test_checks.py     # core.W001 system check (email backend guard)
    test_models.py     # SiteSettings and AboutProfile singletons
    test_templatetags.py  # first_paragraph filter
    test_views.py      # admin, sitemap, robots.txt
  contact/
    test_admin.py      # no-add permission for inquiries
    test_forms.py      # form validation, POST, email-failure resilience
    test_models.py     # ContactInquiry default status
    test_views.py      # contact GET, success page, query param prefill
  e2e/
    conftest.py        # live server + browser fixtures
    test_contact.py    # contact submit/success flow
    test_homepage.py   # homepage smoke
    test_navigation.py # mobile navigation
    test_projects.py   # project list usability
    test_services.py   # services seeded-content flow
  pages/
    test_views.py      # home/about pages and featured-project exclusion
  projects/
    test_admin.py      # admin thumbnail helpers
    test_models.py     # Project, ProjectImage, Testimonial
    test_views.py      # list, detail, context, query count, og_image fallback
  services/
    test_models.py     # Service str, slug, deliverables
    test_views.py      # services page
```

```bash
uv run pytest                       # fast pytest suite (excludes e2e by default)
uv run pytest -x                    # stop on first failure
uv run pytest tests/projects/       # one domain
uv run pytest tests/contact/test_forms.py  # one file
uv run playwright install chromium  # install the browser once locally
uv run pytest tests/e2e --override-ini="addopts=-v --tb=short" -m e2e --browser chromium
```

### Coverage

```bash
make coverage
# or: uv run pytest --cov --cov-report=term-missing
```

Current baseline (at time of writing): **99 % coverage** (480 statements, 1 missed).
The number may shift as features are added; run `make coverage` to see the current figure.
Coverage is also reported in CI on every push.

### pre-commit hooks

Install hooks into your local git repo (one-time):

```bash
uv run pre-commit install
```

Hooks run automatically on `git commit`. To run manually against all files:

```bash
uv run pre-commit run --all-files
```

Hooks configured:

- `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-toml`
- `check-merge-conflict`, `check-added-large-files`, `debug-statements`
- `no-commit-to-branch` (protects `main`)
- `ruff check` + `ruff-format`

### Makefile shortcuts

```bash
# Development
make run           # start dev server
make migrate       # apply migrations
make migrations    # create new migrations
make superuser     # create admin user interactively
make seed          # seed demo content
make collectstatic # collect static files
make tree          # print project tree

# Code quality
make lint          # ruff check (no fix)
make fmt           # ruff check --fix + ruff format
make typecheck     # mypy
make test          # pytest (excludes e2e by default)
make test-e2e      # Playwright browser tests in Chromium
make health        # ruff + mypy + pytest + Django checks + dep drift
make coverage      # pytest --cov --cov-report=term-missing
make check-deploy  # manage.py check --deploy (prod settings)
make smoke         # smoke-check a running instance via SMOKE_BASE_URL
make check-reqs   # verify requirements.txt matches pyproject.toml
make reqs         # regenerate requirements.txt after dep changes

# Clean
make clean-db      # delete db.sqlite3 (prompts for confirmation)
make clean-media   # delete media/ uploads (prompts for confirmation)
make clean-all     # everything (prompts for confirmation)
```

---

## Project structure

```text
jeannote/
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI
├── config/
│   ├── settings/
│   │   ├── base.py            # shared settings
│   │   ├── dev.py             # development overrides
│   │   └── prod.py            # production hardening
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                      # all first-party Django apps
│   ├── core/                  # site-wide glue: global models, checks, context processor, sitemaps
│   │   ├── admin/
│   │   ├── models/            # SiteSettings, AboutProfile (singletons)
│   │   ├── templatetags/
│   │   │   └── core_tags.py   # first_paragraph filter
│   │   ├── management/commands/
│   │   │   └── seed_demo.py
│   │   ├── migrations/
│   │   ├── checks.py          # core.W001 — email backend guard
│   │   ├── context_processors.py
│   │   ├── sitemaps.py
│   ├── pages/                 # static content pages (home + about)
│   │   ├── apps.py
│   │   ├── views.py           # HomeView, AboutView
│   │   ├── urls.py
│   │   ├── templates/
│   │   │   └── pages/
│   ├── projects/              # portfolio projects domain
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── templates/
│   │   │   └── projects/
│   │   ├── migrations/
│   │   ├── sitemaps.py
│   │   └── urls.py
│   ├── contact/               # contact form domain
│   │   ├── admin.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── templates/
│   │   │   └── contact/
│   │   ├── migrations/
│   │   └── urls.py
│   └── services/              # services listing domain
│       ├── admin.py
│       ├── models.py
│       ├── views.py
│       ├── templates/
│       │   └── services/
│       ├── migrations/
│       └── urls.py
├── templates/                 # project-level shell templates (base, nav, footer)
│   ├── base.html
│   ├── robots.txt
│   └── includes/
│       ├── nav.html
│       └── footer.html
├── static/
│   ├── css/main.css           # design system (CSS custom properties)
│   ├── js/main.js
│   └── images/
├── tests/                     # domain-structured test suite (mirrors apps/)
│   ├── conftest.py
│   ├── core/
│   ├── contact/
│   ├── pages/
│   ├── projects/
│   └── services/
├── scripts/
│   ├── smoke_check.py
│   └── tree.py
├── media/                     # local uploaded files (gitignored)
├── pyproject.toml             # authoring source for all dependencies
├── uv.lock                    # locked dependency graph (do not edit by hand)
├── requirements.txt           # generated deployment export — run: make reqs
├── Dockerfile                 # local dev container (not for production)
├── compose.yml                # docker compose for local dev
├── .dockerignore
├── Makefile
├── Procfile                   # gunicorn entry point
├── railway.toml               # Railway deployment config
├── .python-version            # Python version pin (3.13)
├── .pre-commit-config.yaml
└── .env.example
```

---

## Template layout

Templates are split across two locations with distinct ownership:

| Location | Owns | Purpose |
| --- | --- | --- |
| `templates/` | Project level | Shell and global chrome — `base.html`, nav, footer, `robots.txt` |
| `apps/pages/templates/pages/` | `pages` app | Home and about page templates |
| `apps/projects/templates/projects/` | `projects` app | Project list and detail |
| `apps/contact/templates/contact/` | `contact` app | Contact form and success page |
| `apps/services/templates/services/` | `services` app | Services listing |

Django's `APP_DIRS=True` loader finds app-level templates automatically. The project-level `templates/` directory holds only the structural chrome (layout, navigation, brand) shared across all apps.

---

## Data models

| Model | Purpose |
| --- | --- |
| `SiteSettings` | Global metadata: name, tagline, contact, social links, SEO, analytics |
| `AboutProfile` | About page: biography, philosophy, portrait, CV file |
| `Service` | Service offering with description, deliverables, and ordering |
| `Project` | Portfolio project with full story structure and SEO fields |
| `ProjectImage` | Gallery images per project with type classification |
| `Testimonial` | Client quotes with optional project association |
| `ContactInquiry` | Submitted contact forms — managed entirely in admin |

`SiteSettings` and `AboutProfile` are **singleton models** (only one row each).

---

## Pages

| URL | View | Purpose |
| --- | --- | --- |
| `/` | `HomeView` | Hero, featured projects, philosophy, services, trust, CTA |
| `/projects/` | `ProjectListView` | Paginated listing with category filter |
| `/projects/<slug>/` | `ProjectDetailView` | Full project case study with gallery |
| `/about/` | `AboutView` | Profile, biography, philosophy, credentials |
| `/services/` | `ServicesView` | Detailed service descriptions |
| `/contact/` | `contact_view` | Enquiry form — saves to DB and emails |
| `/contact/thank-you/` | `contact_success_view` | Post-submission confirmation |
| `/admin/` | Django admin | Full content management |

---

## Environment variables

All configuration is via environment variables (read from `.env` locally,
or injected by your hosting platform in production). See `.env.example` for
the complete annotated list.

| Variable | Required | Default | Notes |
| --- | --- | --- | --- |
| `SECRET_KEY` | **Yes** | — | Generate with Django's `get_random_secret_key()` |
| `DEBUG` | No | `True` | Always `False` in production |
| `ALLOWED_HOSTS` | **Prod** | `localhost,127.0.0.1` | Comma-separated hostname list |
| `DJANGO_SETTINGS_MODULE` | **Prod** | `config.settings.dev` | Set to `config.settings.prod` |
| `DATABASE_URL` | **Prod** | SQLite | `postgres://user:pass@host/db` |
| `EMAIL_BACKEND` | **Prod** | Console backend | Must be SMTP in production ⚠️ |
| `EMAIL_HOST` | If SMTP | — | SMTP hostname |
| `EMAIL_PORT` | If SMTP | `587` | Usually 587 (TLS) or 465 (SSL) |
| `EMAIL_USE_TLS` | If SMTP | — | Set `True` for port 587 |
| `EMAIL_HOST_USER` | If SMTP | — | SMTP login username |
| `EMAIL_HOST_PASSWORD` | If SMTP | — | SMTP login password |
| `DEFAULT_FROM_EMAIL` | No | = `CONTACT_EMAIL` | "From" address on outgoing mail |
| `CONTACT_EMAIL` | No | `contact@jeannot-tsirenge.com` | Receives contact form notifications |
| `CSRF_TRUSTED_ORIGINS` | **Prod** | `[]` | Required behind HTTPS reverse proxies |
| `SENTRY_DSN` | Recommended | — | Enables Sentry exception capture in production |
| `SENTRY_ENVIRONMENT` | No | `production` | Environment name reported to Sentry |
| `SENTRY_RELEASE` | No | — | Release/commit identifier shown on Sentry events |
| `SENTRY_TRACES_SAMPLE_RATE` | No | `0.0` | Performance tracing sample rate from `0.0` to `1.0` |
| `SENTRY_SEND_DEFAULT_PII` | No | `False` | Leave off unless you explicitly want request/user PII |

---

## Production deployment

> **Status:** Railway is the first deployment target. The `Procfile` (gunicorn) and `railway.toml` are committed and ready. The first deploy is manual. Production media is already wired to Cloudinary in `prod.py`, but the required Cloudinary credentials and real SMTP settings must be present in the deployment environment before launch.

### 1. Activate production settings

Set in your hosting platform's environment:

```text
DJANGO_SETTINGS_MODULE=config.settings.prod
```

This enables `DEBUG=False`, HSTS, SSL redirect, and secure cookies. **Do not deploy without this.**

### 2. Minimum required environment variables

```dotenv
SECRET_KEY=<long-random-string>
DJANGO_SETTINGS_MODULE=config.settings.prod
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgres://user:password@host:5432/dbname
CONTACT_EMAIL=contact@jeannot-tsirenge.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

### 3. Email — must configure before launch ⚠️

> Without a real email backend, the architect receives no notification when
> a contact form is submitted. Enquiries are saved to the database but arrive
> silently.

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
DEFAULT_FROM_EMAIL=Jeannot Tsirenge <contact@jeannot-tsirenge.com>
```

Recommended providers: SendGrid, Mailgun, Postmark, Amazon SES.

### 3a. Error visibility — enable before launch

Sentry is now supported in `config.settings.prod` and initializes only when
`SENTRY_DSN` is present. The smallest correct production setup is:

```dotenv
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_ENVIRONMENT=production
SENTRY_RELEASE=<git-sha-or-release-name>
```

`SENTRY_TRACES_SAMPLE_RATE` defaults to `0.0`, so this starts with exception
monitoring only. Increase tracing later only if you want performance data.

### 4. Media file persistence — must resolve before uploading real content ⚠️

> On ephemeral platforms (Railway and similar) uploaded files are deleted on
> every deploy. The default local-filesystem storage is not suitable for
> production use. **This must be resolved before any real images are uploaded
> to a live environment.**

This repo already resolves that in production by setting:

```python
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
```

To make uploads durable in production, set these three environment variables:

```dotenv
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

If those are missing, admin-managed uploads will fail at runtime. Static files
are a separate concern and continue to be served by Whitenoise.

### 5. Static files

Static files are served by [Whitenoise](https://whitenoise.readthedocs.io) — no CDN required. Run once:

```bash
make collectstatic
```

### 6. First-time deployment steps

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py collectstatic --noinput
# optional:
uv run python manage.py seed_demo
```

Then log in to `/admin/` to configure Site Settings, upload images, and replace demo content.

### 7. Pre-launch verification

```bash
# Repo health gate
make health

# Production security/config audit (should pass cleanly)
make check-deploy

# Smoke-check a running instance after deploy
SMOKE_BASE_URL=https://yourdomain.com make smoke
```

`make check-deploy` now injects dummy-but-valid values for production-only
environment variables so that warnings are real misconfigurations, not noise
from the local shell. If it warns, fix the underlying production setting.

### 8. Deployment checklist

- [ ] `DJANGO_SETTINGS_MODULE=config.settings.prod`
- [ ] Long unique `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` set to live domain(s)
- [ ] `DATABASE_URL` pointing to PostgreSQL
- [ ] `CSRF_TRUSTED_ORIGINS` set
- [ ] SMTP email backend configured and tested
- [ ] `CONTACT_EMAIL` set to a monitored inbox
- [ ] Cloudinary credentials set for production media uploads
- [ ] `SENTRY_DSN` set for production exception visibility
- [ ] `collectstatic` and `migrate` run
- [ ] Admin superuser created
- [ ] Real portrait and OG image uploaded in admin
- [ ] Site Settings completed (email, phone, location, social links)
- [ ] Demo testimonials replaced with real client quotes (or clearly marked)
- [ ] `make check-deploy` passes cleanly
- [ ] `SMOKE_BASE_URL=https://yourdomain.com make smoke` passes after deploy

---

## Continuous integration

A GitHub Actions workflow ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs on every push and pull request:

| Step | Command |
| --- | --- |
| Lint | `uv run ruff check .` |
| Type check | `uv run mypy .` |
| Tests + coverage | `uv run pytest --cov --cov-report=term-missing` |
| Django system check | `uv run python manage.py check` |
| Migration drift check | `uv run python manage.py makemigrations --check --dry-run` |
| Deploy check | `make check-deploy` |
| Dep drift check | `make check-reqs` |

CI uses `config.settings.dev` (SQLite, console email) with a dummy `SECRET_KEY`. No deployment step is wired — deploys are manual by design until the production media and SMTP configuration is confirmed.

---

## Roadmap (Version 2)

- [ ] Blog / journal section
- [ ] Project PDF download sheets
- [ ] Bilingual / multilingual support (French + English)
- [ ] Press & publications section
- [ ] Awards section
- [ ] Consultation booking / calendar integration
- [ ] Newsletter signup
- [ ] Advanced project search / full-text filtering
