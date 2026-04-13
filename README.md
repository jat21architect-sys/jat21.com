# Architecture Portfolio — Django Template

A professional, content-driven portfolio platform for architecture practices, built with Django.

> **New here?** See [SETUP.md](SETUP.md) for the buyer-facing setup and customisation checklist.
>
> **Current stable version:** `v1.0.2`\
> **Status:** Stable\
> **Stack:** Python `3.13` · Django `5.2 LTS`\
> **Docs:** [SETUP.md](SETUP.md) · [DEMO.md](DEMO.md) · [CHANGELOG.md](CHANGELOG.md) · [LICENSE.md](LICENSE.md)\
> **Theme guide:** [docs/specs/TOKENS.md](docs/specs/TOKENS.md)\
> **Maintainers:** [RELEASE.md](RELEASE.md)

---

## What this is

A production-ready Django template for architecture practices who want a content-managed
portfolio site — not a generic website builder, not a theme on top of a CMS, but a
properly engineered Django application built specifically for this domain.

**Buy it. Clone it. Fill in your content. Ship it.**

Everything needed to take a practice from no web presence to a live, professional site
is already built and tested. You own the code outright — customise anything.

---

## Who it's for

- Sole-practitioner architects or small studios
- Graduates establishing an independent practice
- Established practices replacing a dated or off-brand site
- Developers or agencies building portfolio sites for architecture clients

Not a good fit if you need multi-tenant, e-commerce, or blog publishing — this is a
focused tool for a specific purpose.

---

## What's included

### Pages

| Page | What it does |
| --- | --- |
| **Home** | Hero, featured projects, homepage coda CTA |
| **Projects** | Paginated portfolio grid with category filter |
| **Project detail** | Full project case study — narrative, gallery, testimonials, SEO |
| **About** | Practice identity, narrative, professional profile, optional portrait, optional CV download |
| **Services** | Detailed service descriptions with deliverables |
| **Contact** | Enquiry form with spam protection, saves to DB, emails on submission |

### Admin

Full Django admin for every model — no custom frontend needed to manage content.

| Model | What you manage |
| --- | --- |
| **Site Settings** | Brand, contact details, social links, SEO, analytics — all in one place |
| **About Profile** | About page content and portrait |
| **Services** | Services listing with ordering and active/inactive toggle |
| **Projects** | Portfolio projects with full story fields, gallery images, and testimonials |
| **Contact Inquiries** | Submitted enquiries — read, manage, and track status |

### Production features

- **Cloudinary integration** — uploaded media is durable across deploys (Railway-safe)
- **PostgreSQL-ready** — SQLite for dev, Postgres for production, configured via `DATABASE_URL`
- **Sentry integration** — exception monitoring in production, opt-in via `SENTRY_DSN`
- **Sitemap** — auto-generated XML sitemap for all projects and pages
- **SEO fields** — per-page meta description and OG image on every model
- **Google Analytics** — GA4 measurement ID managed in admin, no code changes
- **SMTP email** — configurable email backend; contact form emails on every submission
- **Content readiness check** — management command flags blank fields, starter/demo content, and stale page-specific metadata before launch
- **Whitenoise static serving** — no CDN required for static files

### Developer ergonomics

- **100+ automated tests** across pytest, pytest-django, and Playwright
- **Playwright e2e tests** for the contact form and key user journeys
- **GitHub Actions CI** — lint, type-check, tests, migration check, deploy check on every push
- **pre-commit hooks** — ruff, trailing whitespace, merge conflict detection
- **`make health`** — one command to run the full quality gate locally
- **Docker + Compose** — reproducible local start-up on macOS/Windows without installing Python

---

## Quick start

```bash
git clone <repo-url>
cd <project-directory>
uv sync --group dev
cp .env.example .env          # then set SECRET_KEY
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py seed_demo   # loads starter/demo content
uv run python manage.py runserver
```

Site at **<http://127.0.0.1:8000>** · Admin at **<http://127.0.0.1:8000/admin>**

See [SETUP.md](SETUP.md) for the full phase-by-phase guide from first run to live site.
See [DEMO.md](DEMO.md) to stand up a preview instance or share a demo URL.
See [CHANGELOG.md](CHANGELOG.md) for what's included in this release.
See [LICENSE.md](LICENSE.md) for purchase terms.

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

## Repo architecture

This repo separates reusable Django apps from repo-level composition.
Reusable shell and domain apps live under `apps/`; shared project config
and page composition live outside `apps/` so domain concerns do not leak
into the cross-cutting layers.

| Path | Ownership |
| --- | --- |
| `config/` | Django project package: settings split, root URLs, ASGI/WSGI. |
| `apps/core/` | Cross-cutting Django glue only: system checks, context processor, templatetags, and other tiny shared helpers. |
| `apps/site/` | Site-wide content/config/admin behavior: `SiteSettings`, `AboutProfile`, readiness rules, and seed/readiness commands. This app keeps the historical Django app label `core` for migration continuity. |
| `apps/pages/` | Public page composition for Home, About, and Privacy, plus page-scoped CSS. Keep it thin. |
| `apps/projects/` | Reusable portfolio / case-study domain. Owns its templates and CSS. |
| `apps/services/` | Reusable services domain and service-specific enquiry context. Owns its templates and CSS. |
| `apps/contact/` | Reusable enquiry flow, persistence, and delivery handling. Owns its templates and CSS. |
| `templates/` | Repo-level shared shell and global chrome: `base.html`, shared nav/footer, error templates, and `robots.txt`. |
| `static/` | Repo-level shared shell assets. Shared CSS stays under `static/css/` with shallow `base/`, `components/`, and `utilities/` grouping plus one `main.css` entrypoint. |
| `tests/` | Repo-level test suite organised by domain and test layer. |
| `docs/` | Repo-level implementation, QA, and admin documentation system. |
| `scripts/` | Operational helpers and local audit scripts. Treat durable scripts differently from ad hoc audits; do not assume everything here is a reusable platform tool. |

### Structural rules

- Add a new Django app only when a real content/workflow domain needs one.
- Reusable/domain apps own their templates and route-specific static assets. The shared shell stays repo-level in `templates/` and `static/`.
- `apps/core` stays small: checks, context processors, templatetags, and tiny shared glue only.
- Site-wide content/config/admin behavior belongs in `apps/site/`, not in `apps/core`.
- Page composition belongs in `apps/pages/`, not in `apps/site/`.
- Do not make a surface reusable unless more than one real project proves the boundary is stable.
- If a new feature is global only because it is configured once, that still does **not** automatically make `apps/core` the right home; use `apps/site` for site-wide content/config or create a new domain app if it owns a real workflow or content model.

---

## Local setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (`brew install uv` or see docs)

See [SETUP.md](SETUP.md) for the full phase-by-phase guide from first run to live site, including environment configuration, admin content phases, email setup, and production deployment.

---

## Run locally with Docker

An alternative to the `uv` setup above. Useful for reproducible local start-up
across macOS and Windows without installing Python or uv on the host.

### Docker requirements

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
    test_checks.py     # core.W001 system check (email backend guard)
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
  site/
    test_admin.py      # SiteSettings / AboutProfile admin guardrails
    test_management_commands.py  # launch-readiness and seed commands
    test_models.py     # SiteSettings and AboutProfile singletons
```

```bash
uv run pytest                       # fast pytest suite (excludes e2e by default)
uv run pytest -x                    # stop on first failure
uv run pytest tests/projects/       # one domain
uv run pytest tests/contact/test_forms.py  # one file
uv run playwright install chromium  # install the browser once locally
uv run pytest tests/e2e --override-ini="addopts=-v --tb=short" -m e2e --browser chromium
```

`uv run pytest` excludes browser tests by default — use `make test-e2e` for the Playwright suite. CI runs both.

### Coverage

```bash
make coverage
# or: uv run pytest --cov --cov-report=term-missing
```

Run `make coverage` to see the current figure.
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

## Management commands

Six custom commands handle content bootstrap, media import, and readiness checking.

| Command | Use for | Safe on production | Idempotent | Key flags |
| --- | --- | --- | --- | --- |
| `seed_demo` | Generic starter content for new installs | Yes | Yes (`get_or_create`) | — |
| `seed_about` | `AboutProfile` skeleton | Yes | Yes — skips non-blank fields | `--force` to overwrite existing |
| `seed_services` | `Service` records | Yes | Yes — skips non-blank fields | `--reset` deletes and reinitialises all |
| `bootstrap_project` | Create one project from local files | Yes | No — creates a new record each run | **`--dry-run` required first** |
| `import_project_images` | Attach images to an existing project | Yes | Yes — deduplicates by filename | **`--dry-run` required first** |
| `check_content_readiness` | Pre-launch content audit | Yes | Yes (read-only) | — |

### Safe production bootstrap order

1. `migrate` + `createsuperuser`
2. `seed_demo` — loads starter/demo content so the site renders on first visit
3. Log in to `/admin/` and replace starter copy with your real content
4. `seed_about` — optional; fills only blank `AboutProfile` fields if you prefer incremental setup
5. `bootstrap_project --dry-run …` then live run for each new project
6. `import_project_images --dry-run …` then live run to attach images

> `seed_demo` is idempotent and loads the shipped starter/demo dataset — it is safe to
> run on a fresh production database to get the site rendering immediately.
> `check_content_readiness` will continue to flag that demo content until you replace it.
> It will update existing records if re-run, so avoid running it after you have replaced
> starter/demo content with your own real content.

---

## Project structure

```text
<repo-root>/
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
├── apps/                      # reusable first-party Django apps
│   ├── core/                  # shared Django runtime glue
│   │   ├── apps.py
│   │   ├── checks.py          # shared deploy/runtime checks
│   │   ├── context_processors.py
│   │   ├── templatetags/
│   │   │   └── core_tags.py
│   ├── site/                  # site-wide content/config/admin behavior
│   │   ├── admin/
│   │   ├── management/commands/
│   │   ├── migrations/
│   │   └── models/            # SiteSettings, AboutProfile (singletons)
│   ├── pages/                 # Home/About/Privacy composition
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── sitemaps.py
│   │   ├── templates/pages/
│   │   └── static/css/
│   ├── projects/              # portfolio projects domain
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── templates/
│   │   │   └── projects/
│   │   ├── static/css/
│   │   │   ├── project-cards.css
│   │   │   └── project-detail.css
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
│   │   ├── static/css/
│   │   │   └── contact.css
│   │   ├── migrations/
│   │   └── urls.py
│   └── services/              # services listing domain
│       ├── admin.py
│       ├── models.py
│       ├── views.py
│       ├── templates/
│       │   └── services/
│       ├── static/css/
│       │   └── services.css
│       ├── migrations/
│       └── urls.py
├── templates/                 # repo-level shared shell
│   ├── base.html
│   ├── robots.txt
│   └── includes/
│       ├── header.html
│       └── footer.html
├── static/                    # repo-level shared shell assets
│   ├── css/
│   │   ├── base/
│   │   ├── components/
│   │   ├── utilities/
│   │   └── main.css
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
| `templates/` | Repo level | Shared shell and global chrome — `base.html`, nav, footer, errors, `robots.txt` |
| `static/` | Repo level | Shared shell CSS, JS, and shared images |
| `apps/pages/templates/pages/` | `pages` app | Home, About, and Privacy composition templates |
| `apps/projects/templates/projects/` | `projects` app | Project list and detail |
| `apps/contact/templates/contact/` | `contact` app | Contact form and success page |
| `apps/services/templates/services/` | `services` app | Services listing |

Django's `APP_DIRS=True` loader finds app-level templates automatically. The shared shell stays repo-level, `apps/pages` owns page composition, and domain apps own their route templates.

---

## Data models

| Model | Purpose |
| --- | --- |
| `SiteSettings` | Global metadata: name, tagline, contact, social links, SEO, analytics |
| `AboutProfile` | About page: identity, narrative, professional profile, optional portrait, optional CV file |
| `Service` | Service offering with description, deliverables, and ordering |
| `Project` | Portfolio project with full story structure and SEO fields |
| `ProjectImage` | Gallery images per project with type classification |
| `Testimonial` | Client quotes with optional project association |
| `ContactInquiry` | Submitted contact forms — managed entirely in admin |

`SiteSettings` and `AboutProfile` are **singleton models** (only one row each).

---

## URL routes

| URL | View | Purpose |
| --- | --- | --- |
| `/` | `HomeView` | Hero, featured projects, homepage coda CTA |
| `/projects/` | `ProjectListView` | Paginated listing with category filter |
| `/projects/<slug>/` | `ProjectDetailView` | Full project case study with gallery |
| `/about/` | `AboutView` | Practice identity, narrative, approach, and professional profile |
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
| `CONTACT_EMAIL` | **Prod** | — | Receives contact form notifications |
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
CONTACT_EMAIL=hello@yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

### 3. Email — must configure before launch ⚠️

> Without a real email backend, the architect receives no notification when
> a contact form is submitted. Enquiries are saved to the database but arrive
> silently.

This template intentionally separates:

- the public email shown on the site: `Site Settings.contact_email`
- the inbox that receives contact-form notifications: `CONTACT_EMAIL`
- the sender shown on outgoing emails: `DEFAULT_FROM_EMAIL`

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-api-key
DEFAULT_FROM_EMAIL=Your Name <hello@yourdomain.com>
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

This section is the deploy-reference view of verification commands.
For the ordered buyer launch path, use [SETUP.md](SETUP.md).
For the maintainer release-tag procedure and command truth, use [RELEASE.md](RELEASE.md).

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

Use the root guides that own these workflows instead of maintaining a second
process checklist here:

- Buyer onboarding and launch path: [SETUP.md](SETUP.md)
- Maintainer release-tag procedure and command truth: [RELEASE.md](RELEASE.md)

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
