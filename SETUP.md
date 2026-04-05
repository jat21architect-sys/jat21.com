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

# 5. Load starter/demo content so the site renders on first visit
uv run python manage.py seed_demo

# 6. Start the dev server
uv run python manage.py runserver
```

Visit **<http://127.0.0.1:8000>** and confirm the site loads.
Visit **<http://127.0.0.1:8000/admin>** and log in with the credentials you just created.

`seed_demo` loads the shipped demo dataset: `Site Settings`, `About Profile`,
three active services, eleven example projects (seven featured), testimonials,
and the tracked demo-media bundle when available.

---

## Phase 2 — Brand and site identity

### Admin → Site Settings

Replace every placeholder with your real information.

| Field | What to enter | Notes |
| --- | --- | --- |
| `site_name` | Your practice name | e.g. "Studio Rossi Architecture" |
| `tagline` | One-line positioning statement | Shown in the homepage hero and footer |
| `hero_label` | Optional short descriptor above the homepage title | e.g. "Architecture & Urbanism" |
| `nav_name` | Optional short navbar brand override | Use if the full `site_name` is too long or the automatic monogram is weak |
| `logo` | Upload your logo | Replaces text branding in the navbar |
| `contact_email` | Public email shown on the site | Shown in the footer and contact page. Contact-form notifications are configured separately via `CONTACT_EMAIL` |
| `phone` | Your contact number | Optional — leave blank to hide |
| `location` | City, Country | Displayed in footer and contact page |
| `address` | Full postal address | Stored in admin only in the current implementation |
| `contact_response_time` | Public response-time wording | Used on the Contact page and success state, e.g. "two working days" |
| `og_image` | Default social share image | Used when no project cover image exists — 1200 × 630 px recommended |
| `meta_description` | Homepage SEO description | Keep under 160 characters |

**Per-page SEO descriptions** (all optional — add if you want control over how each
page appears in search results):

- `about_meta_description`
- `services_meta_description`
- `projects_meta_description`
- `contact_meta_description`

If you do set a page-specific meta description, make sure it matches the current
studio identity. The launch-readiness check now flags stale per-page metadata
that still names an old demo studio.

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

### Admin → About Profile

Start with the fields that shape the public identity of the practice:

| Field | What to enter | Notes |
| --- | --- | --- |
| `identity_mode` | `studio` or `person` | Choose whether the page introduces the studio or a named principal |
| `principal_name` | Public principal name | Required only for person-led mode |
| `principal_title` | Public role/title | Used in the hero meta line for person-led mode |
| `practice_structure` | Truthful short descriptor | e.g. "Solo practice" or "Small studio" |
| `one_line_practice_description` | Short public one-liner | Shown in the About hero |

Then complete the main narrative:

| Field | What to enter | Notes |
| --- | --- | --- |
| `practice_summary` | What the practice does and what kind of work it takes on | Main opening prose block |
| `project_leadership` | How projects are led and where collaborators fit | Secondary narrative block |
| `approach` | Short practical approach statement | 2–3 sentences is ideal |
| `closing_invitation` | Short closing CTA copy | If kept under 80 characters it becomes the CTA heading |

Then fill the credibility block:

| Field | What to enter | Notes |
| --- | --- | --- |
| `professional_standing` | Registration or professional standing | Publicly shown when complete |
| `education` | One fact per line | e.g. degrees, formal training |
| `supporting_facts` | One factual proof point per line | e.g. sectors worked in, delivery scope, awards if real |
| `experience_years` | Your actual years of practice | This renders publicly as `N+ years in practice` |

Portrait and file options:

| Field | What to enter | Notes |
| --- | --- | --- |
| `portrait_mode` | `text_only` or `portrait` | Use text-only until you have a real portrait ready |
| `portrait` | Upload a real portrait | Required for the portrait column to render |
| `cv_file` | Optional PDF profile/CV | Only appears when the portrait column is visible |

---

## Phase 4 — Services

### Admin → Services

Three starter service records are loaded by `seed_demo`. Edit them to match your
actual offering, or delete and create your own.

For each service:

| Field | What to enter |
| --- | --- |
| `title` | Service name, e.g. "Housing" or "Feasibility Studies" |
| `summary` | One-sentence description shown on cards (under 250 characters) |
| `description` | Full explanation of the service |
| `who_for` | Who this is best suited to, e.g. "Homeowners planning a new build" |
| `value_proposition` | What the client gains |
| `deliverables` | One deliverable per line, e.g. "Concept drawings", "Planning submission" |
| `slug` | Usually leave the prepopulated slug alone | The Services page uses it for section anchors and contact-form prefill mapping |
| `order` | Controls display order; lower numbers appear first |
| `active` | Uncheck to hide a service without deleting it |

---

## Phase 5 — Projects

### Admin → Projects

`seed_demo` loads eleven example projects, seven of them featured. Replace the
demo records with your real work before launch, or add your own projects directly
in admin.

For each project:

### Core

| Field | What to enter |
| --- | --- |
| `title` | Project name |
| `short_description` | 1–2 sentences for cards and search results (under 160 characters ideal) |
| `category` | `Housing` / `Civic` / `Workplace` |
| `status` | Completed / In Progress / Concept / Competition Entry |

### Metadata

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

### Media

| Field | What to enter |
| --- | --- |
| `cover_image` | Hero image — at least 1600 × 900 px, JPEG or WebP |
| Project Images (inline) | Gallery images — add as many as needed |

### Display flags

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

Each project can have testimonials attached inline. Add the author name, role, company,
quote, order, and active state.

### Adding many projects from local files

The `bootstrap_project` and `import_project_images` commands can create projects and
attach gallery images from local files. Both commands require absolute file paths.
Always run `--dry-run` first:

```bash
uv run python manage.py bootstrap_project \
  --dry-run \
  --title "House Aldea" \
  --category residential \
  --short-description "Private residence on a constrained urban site." \
  --cover /absolute/path/to/cover.jpg \
  --gallery /absolute/path/to/gallery-01.jpg /absolute/path/to/gallery-02.jpg

uv run python manage.py import_project_images \
  --dry-run \
  --project house-aldea \
  --gallery /absolute/path/to/gallery-03.jpg /absolute/path/to/gallery-04.jpg
```

---

## Phase 6 — Email

Contact form submissions are always saved to the database and visible in Admin → Contact
Inquiries, regardless of whether email is configured. **If you skip this phase or leave
`CONTACT_EMAIL` unset, submissions will be saved but no notification email will be sent to
you.** Configure `CONTACT_EMAIL` before launch to enable delivery notifications.

To also set up email notifications, configure an SMTP backend and set the following
variables. There are three separate email roles in this template:

- `Site Settings.contact_email`: the public email shown on the site
- `CONTACT_EMAIL`: the inbox that receives contact-form notification emails
- `DEFAULT_FROM_EMAIL`: the sender shown on outgoing notification emails

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
or still set to starter/demo values:

```bash
uv run python manage.py check_content_readiness
```

The command uses two output levels:

| Output | Meaning | Action |
| --- | --- | --- |
| `✗` (blocker) | Must be fixed before launch — site will look broken or still contain demo values | Fix before deploying |
| `⚠` (warning) | Does not block launch but degrades quality or trust | Fix if time allows |
| All clear | No issues found | Proceed to Phase 8 |

The command exits with code `1` if any blocker is present (CI-friendly).

**Common first-run blockers and where to fix them:**

| Blocker message | Where to fix |
| --- | --- |
| `site_name` is still the demo value | Admin → Site Settings → Identity |
| `contact_email` is still the demo value | Admin → Site Settings → Contact |
| `one_line_practice_description` is blank or demo copy | Admin → About Profile → Identity |
| `practice_summary` is blank or demo copy | Admin → About Profile → Content |
| Demo project titles detected | Admin → Projects — replace or delete the seeded examples |

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
| `seed_demo` | Fresh install — loads the starter/demo dataset |
| `check_content_readiness` | Before launch — flags blocking launch issues, demo values, and stale page metadata |
| `bootstrap_project` | Add a project from local files |
| `import_project_images` | Attach a batch of images to an existing project |
| `seed_about` | Optionally fill blank AboutProfile fields incrementally |
| `seed_services` | Optionally reset service records to the starter set |
