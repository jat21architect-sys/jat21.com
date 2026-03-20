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
| Dependency management | [uv](https://docs.astral.sh/uv/) |
| Linting / formatting | [Ruff](https://docs.astral.sh/ruff/) |
| Type checking | mypy + django-stubs |
| Testing | pytest + pytest-django |
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

### Tests

```bash
uv run pytest                # all tests
uv run pytest -x             # stop on first failure
uv run pytest tests/test_views.py   # one file
```

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
make run           # start dev server
make migrate       # apply migrations
make migrations    # create new migrations
make superuser     # create admin user interactively
make seed          # seed demo content
make collectstatic # collect static files
make tree          # print project tree
make clean         # remove __pycache__, staticfiles artefacts
make clean-db      # delete db.sqlite3 (prompts for confirmation)
make clean-media   # delete media/ uploads (prompts for confirmation)
make clean-all     # everything (prompts for confirmation)
```

---

## Project structure

```text
jeannote/
├── config/
│   ├── settings/
│   │   ├── base.py        # shared settings
│   │   ├── dev.py         # development
│   │   └── prod.py        # production
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── portfolio/             # main application
│   ├── models.py          # all data models
│   ├── admin.py           # content management
│   ├── views.py           # page views
│   ├── urls.py            # URL routing
│   ├── forms.py           # contact form
│   ├── context_processors.py
│   └── management/commands/seed_demo.py
├── templates/             # HTML templates
├── static/
│   ├── css/main.css       # complete design system (CSS custom properties)
│   └── js/main.js         # minimal vanilla JS
├── tests/
│   ├── conftest.py        # shared fixtures
│   ├── test_views.py      # page / route tests
│   ├── test_models.py     # model unit tests
│   └── test_forms.py      # form validation + contact POST
├── scripts/tree.py        # repository tree printer
├── pyproject.toml         # dependencies and tool configuration (source of truth)
├── uv.lock                # locked dependency graph (source of truth)
├── requirements.txt       # generated for compatibility (do not edit by hand — run: uv export --no-dev --no-hashes -o requirements.txt)
├── .python-version        # Python version pin
├── .pre-commit-config.yaml
└── .env.example
```

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

---

## Production deployment

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

### 4. Media file persistence — must resolve before uploading real content ⚠️

> On ephemeral platforms (Heroku, Render, Fly.io, Railway) uploaded files are
> deleted on every deploy. The default local-filesystem storage is not
> suitable for production use.

**Integration point:** look for `# MEDIA_STORAGE_INTEGRATION_POINT` in
[`config/settings/base.py`](config/settings/base.py). To switch to S3:

```bash
uv add "django-storages[s3]"
```

```dotenv
DEFAULT_FILE_STORAGE=storages.backends.s3boto3.S3Boto3Storage
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=af-south-1
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
```

Safe to defer only if the initial deployment uses no uploaded (real) images.

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
# Security audit against production settings.
# Expects exactly one security.W009 warning (dummy SECRET_KEY used locally).
# Any other warnings are real issues that must be fixed before launch.
make check-deploy

make test
```

### 8. Deployment checklist

- [ ] `DJANGO_SETTINGS_MODULE=config.settings.prod`
- [ ] Long unique `SECRET_KEY`
- [ ] `ALLOWED_HOSTS` set to live domain(s)
- [ ] `DATABASE_URL` pointing to PostgreSQL
- [ ] `CSRF_TRUSTED_ORIGINS` set
- [ ] SMTP email backend configured and tested
- [ ] `CONTACT_EMAIL` set to a monitored inbox
- [ ] Media storage strategy resolved (local volume or S3)
- [ ] `collectstatic` and `migrate` run
- [ ] Admin superuser created
- [ ] Real portrait and OG image uploaded in admin
- [ ] Site Settings completed (email, phone, location, social links)
- [ ] Demo testimonials replaced with real client quotes (or clearly marked)
- [ ] `make check-deploy` returns only the expected SECRET_KEY warning (no others)

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
