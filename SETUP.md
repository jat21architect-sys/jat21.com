# Buyer Setup Guide

A step-by-step checklist for taking this template from fresh install to live site.
Work through each phase in order. Everything after Phase 1 happens in the Django admin.

---

## Phase 1 — First run (local)

**Goal:** Get the site running locally so you can see it before making any changes.

```bash
# 1. Clone and install
git clone <repo-url>
cd <project-directory>
uv sync --group dev

# 2. Create your environment file
cp .env.example .env
```

Open `.env` and set `SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the output as the value. Leave everything else as-is for now.

```bash
# 3. Create the database
uv run python manage.py migrate

# 4. Create your admin account
uv run python manage.py createsuperuser

# 5. Load starter content so the site renders on first visit
uv run python manage.py seed_demo

# 6. Start the dev server
uv run python manage.py runserver
```

Visit **<http://127.0.0.1:8000>** and confirm the site loads.
Visit **<http://127.0.0.1:8000/admin>** and log in with the credentials you just created.

---

## Phase 2 — Brand and site identity

**Admin → Site Settings**

Replace every placeholder with your real information.

| Field | What to enter | Notes |
| --- | --- | --- |
| `site_name` | Your practice name | e.g. "Studio Rossi Architecture" |
| `tagline` | One-line positioning statement | Shown in header and meta |
| `contact_email` | Your monitored inbox | Receives contact form notifications |
| `phone` | Your contact number | Optional — leave blank to hide |
| `location` | City, Country | Displayed in footer and contact page |
| `address` | Full postal address | Optional — for footer or contact use |
| `logo` | Upload your logo | Replaces the text site name in the nav |
| `og_image` | Default social share image | Used when no project cover image exists — 1200 × 630 px recommended |
| `meta_description` | Homepage SEO description | Keep under 160 characters |

**Per-page SEO descriptions** (all optional — add if you want control over how each
page appears in search results):

- `about_meta_description`
- `services_meta_description`
- `projects_meta_description`
- `contact_meta_description`

**Social links** (all optional — leave blank to hide the icon):

- `linkedin_url`
- `instagram_url`
- `facebook_url`
- `behance_url`
- `issuu_url`

**Analytics** (optional):

- `google_analytics_id` — paste your GA4 Measurement ID (e.g. `G-XXXXXXXXXX`)

---

## Phase 3 — About page

**Admin → About Profile**

| Field | What to enter | Notes |
| --- | --- | --- |
| `headline` | Your name or practice headline | Shown as the page heading |
| `intro` | 2–4 sentence intro | Shown at the top of the About page |
| `biography` | Full biographical text | Supports multiple paragraphs |
| `philosophy` | Design philosophy statement | Optional section |
| `credentials` | Education, memberships, certifications | One entry per line |
| `experience_years` | Your actual years of practice | **Replace 0 — this renders publicly** |
| `location` | Where you are based | Optional |
| `portrait` | Upload a portrait photo | Recommended minimum: 800 × 800 px |
| `cv_file` | Upload a PDF CV | Optional — enables a CV download link |

---

## Phase 4 — Services

**Admin → Services**

Six placeholder service records are loaded by `seed_demo`. Edit them to match your
actual offering, or delete and create your own.

For each service:

| Field | What to enter |
| --- | --- |
| `title` | Service name, e.g. "Residential Design" |
| `summary` | One-sentence description shown on cards (under 250 characters) |
| `description` | Full explanation of the service |
| `who_for` | Who this is best suited to, e.g. "Homeowners planning a new build" |
| `value_proposition` | What the client gains |
| `deliverables` | One deliverable per line, e.g. "Concept drawings", "Planning submission" |
| `icon_name` | Optional — icon identifier from your chosen icon library |
| `order` | Controls display order; lower numbers appear first |
| `active` | Uncheck to hide a service without deleting it |

---

## Phase 5 — Projects

**Admin → Projects**

Four placeholder projects are loaded by `seed_demo`. Delete them and add your real work,
or add a project directly via admin.

For each project:

**Core**

| Field | What to enter |
| --- | --- |
| `title` | Project name |
| `short_description` | 1–2 sentences for cards and search results (under 160 characters ideal) |
| `category` | Residential / Commercial / Cultural / Interiors / Renovation |
| `status` | Completed / In Progress / Concept / Competition Entry |

**Metadata**

| Field | What to enter |
| --- | --- |
| `location` | Where the project is located |
| `year` | Year completed (or anticipated) |
| `client` | Client name — leave blank if confidential |
| `area` | Floor area, e.g. `2 400 m²` |
| `services_provided` | Scope delivered, e.g. "Concept design through construction administration" |

**Narrative** (all optional — fill as many as apply)

| Field | What to enter |
| --- | --- |
| `overview` | Project introduction |
| `challenge` | The design challenge or brief constraints |
| `concept` | The core design idea |
| `process` | Design and construction process |
| `outcome` | Result and impact |

**Media**

| Field | What to enter |
| --- | --- |
| `cover_image` | Hero image — at least 1600 × 900 px, JPEG or WebP |
| Project Images (inline) | Gallery images — add as many as needed |

**Display flags**

| Field | What to enter |
| --- | --- |
| `featured` | Check to show this project on the homepage |
| `order` | Controls list order within the portfolio; lower numbers appear first |

**SEO overrides** (optional)

| Field | What to enter |
| --- | --- |
| `seo_title` | Overrides the project title in browser tab and search (under 60 characters) |
| `seo_description` | Overrides `short_description` in search results (under 160 characters) |

**Testimonials** (optional — added inline on the project record)

Each project can have testimonials attached. Add author, role, text, and optionally a photo.

### Adding many projects from local files

The `bootstrap_project` and `import_project_images` commands can create projects and
attach gallery images from local directories. Always run `--dry-run` first:

```bash
uv run python manage.py bootstrap_project --dry-run --title "House Aldea" --dir path/to/files
uv run python manage.py import_project_images --dry-run --project-slug house-aldea --dir path/to/images
```

---

## Phase 6 — Email

Contact form submissions are always saved to the database. To also receive email
notifications, configure an SMTP backend before going live.

Open `.env` (or your production environment variables) and set:

```dotenv
# Switch to SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-smtp-username
EMAIL_HOST_PASSWORD=your-smtp-password

# Address in the From field of outgoing emails
DEFAULT_FROM_EMAIL=Studio Rossi <hello@yourdomain.com>

# Address that receives contact form notifications — must be your monitored inbox
CONTACT_EMAIL=hello@yourdomain.com
```

Verify by submitting the contact form locally and checking that you receive the email.

---

## Phase 7 — Content readiness check

Run this before deploying. It scans your database for required fields that are still blank
or at placeholder values:

```bash
uv run python manage.py check_content_readiness
```

Fix every warning it reports. The command exits with code 1 if any warnings remain,
so it can be added to a deployment gate if needed.

---

## Phase 8 — Production environment

Set these variables in your hosting environment (e.g. Railway → Variables):

| Variable | Value |
| --- | --- |
| `SECRET_KEY` | A new unique key — do not reuse your local one |
| `DEBUG` | `False` |
| `DJANGO_SETTINGS_MODULE` | `config.settings.prod` |
| `ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com` |
| `DATABASE_URL` | `postgres://user:password@host:5432/dbname` |
| `CSRF_TRUSTED_ORIGINS` | `https://yourdomain.com,https://www.yourdomain.com` |
| `CONTACT_EMAIL` | Your monitored inbox |
| `EMAIL_BACKEND` | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | Your SMTP server |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | Your SMTP username |
| `EMAIL_HOST_PASSWORD` | Your SMTP password |
| `DEFAULT_FROM_EMAIL` | `Your Name <hello@yourdomain.com>` |

After setting variables and deploying, verify production Django settings:

```bash
make check-deploy
# or: uv run python manage.py check --deploy
```

Fix any warnings before accepting live traffic.

---

## Phase 9 — Go live

Run the content readiness check one final time against production:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check_content_readiness
```

Then smoke-check the live site:

```bash
SMOKE_BASE_URL=https://yourdomain.com make smoke
```

This confirms the main pages return HTTP 200 and no obvious errors appear.

---

## Quick reference — admin sections

| Admin section | What it controls |
| --- | --- |
| **Site Settings** | Brand, contact details, social links, SEO, analytics |
| **About Profile** | About page content and portrait |
| **Services** | Services listing page |
| **Projects** | Portfolio grid and individual project pages |
| **Contact Inquiries** | Submitted enquiries (read and manage) |

## Quick reference — management commands

| Command | When to use |
| --- | --- |
| `seed_demo` | Fresh install — loads generic starter content |
| `check_content_readiness` | Before launch — flags missing or placeholder content |
| `bootstrap_project` | Add a project from local files |
| `import_project_images` | Attach a batch of images to an existing project |
| `seed_about` | Optionally fill blank AboutProfile fields incrementally |
| `seed_services` | Optionally reset service records to the starter set |
