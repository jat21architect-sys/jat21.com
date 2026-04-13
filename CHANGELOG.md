# Changelog

All notable changes to this template are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.2] — 2026-04-12

### Fixed

- **Onboarding docs — secret key command:** All five buyer-facing files (`SETUP.md`, `DEMO.md`,
  `README.md`, `.env.example`, `docs/recovery-runbook.md`) instructed buyers to run
  `python -c "from django.core.management.utils import get_random_secret_key; ..."`. This
  command fails with `ModuleNotFoundError` on any machine where Django is not globally
  installed — the common state after `uv sync`. All occurrences corrected to
  `uv run python -c "..."`, consistent with every other command in these files.
- **Onboarding docs — `seed_demo` framing:** README.md Step 5 labelled `seed_demo` as
  "optional". Without it the site renders blank on first load. Label changed to
  "recommended for first run" with an explicit clarification that skipping it leaves the
  site mostly blank.
- **Onboarding docs — `check_content_readiness` after seed:** SETUP.md Phase 1 gave no
  indication that running `make check-content` immediately after `seed_demo` would show
  nine blockers — all expected, as the starter content is intentionally placeholder.
  A note added making this behaviour explicit and directing buyers to complete Phases 2–6
  before running the check.

### Notes

- No runtime code changes.
- No migration changes.
- No change to the locked `1.0.1` baseline other than documentation corrections.
- Fresh-install drill (`clone → uv sync → .env → migrate → seed_demo → runserver`)
  confirmed all routes return HTTP 200 with no errors on a clean machine.

---

## [1.0.1] — 2026-03-24

### Fixed

- **Content resilience — home page:** Trust section now hidden when no trust data is populated (`experience_years`, `project_count`, active services, location all blank). `project_count` stat item individually guarded so a count of zero does not render a blank stat.
- **Content resilience — footer:** Contact column (`email`, social links) is suppressed entirely when every contact field is blank, preventing an empty column in the footer grid.
- **Content resilience — `site_name` blank:** Six public-facing references to `site_name` now fall back to `"Studio Name"` via `|default` so the site is never visibly broken when the field is empty. Admin warns at save-time when `site_name` is blank.
- **Project detail — no cover image:** Projects without a cover image now render correctly. The hero uses a dark surface, compact height matching `page-hero--short` rhythm, and white text — replacing the previous state where white text appeared on a white background.
- **CSS — contact page (769–960 px):** Contact grid gap reduced from `var(--space-xl)` (7 rem) to `var(--space-lg)` (4 rem) inside the `≤960px` media query. At this range the sidebar narrows to 260 px; the original gap left form fields only ~160 px wide on tablet-portrait viewports.
- **CSS — page hero narrow-phone padding:** About and Services pages use the full `.page-hero` variant whose top-padding (`11.5 rem`) consumed ~33 % of the viewport on 320 px screens. A `≤480px` rule now matches `.page-hero--short` rhythm (`8.5 rem` top) at very small widths.

### Changed

- **Nav mobile overlay:** Link group optical centering adjusted (`padding-block-start: 3 rem`) so the menu items sit at ~48 % of the visible dark area rather than appearing low.

### Hardened (release lock pass — 2026-04-12)

- **Brand logic extracted:** `apps/core/brand.py` is now the single source of truth for `compute_monogram()`, `nav_needs_monogram()`, and `NAV_TEXT_MAX_CHARS`/`NAV_TEXT_MAX_WORDS`. Template tags, admin, and management commands all import from here rather than duplicating the logic.
- **Enquiry vocabulary consolidated:** `apps/core/enquiry_types.py` centralises `PROJECT_TYPE_CHOICES`, `LEGACY_PROJECT_TYPE_MAP`, `SERVICE_SLUG_TO_ENQUIRY_TYPE`, and `PROJECT_CATEGORY_TO_ENQUIRY_TYPE`. Previous duplicates in `contact/forms.py`, `contact/views.py`, `services/models.py`, and `projects/models.py` removed.
- **Duplicate system check ID fixed:** Non-HTTPS CSRF origins check was `core.W002` (duplicate of the empty-CSRF check). Renamed to `core.W007`.
- **Model help_text additions:** `SiteSettings.nav_name` (migration 0010), `SiteSettings.address` (0011), and `Testimonial.project` (projects 0004) now carry help_text clarifying their template-product context to buyers.
- **Version consistency:** Version string aligned to `1.0.1` across `pyproject.toml`, `LICENSE.md`, and `uv.lock`.
- **Static file header residue removed:** Personal name references removed from comment headers in `static/css/main.css`, `static/js/main.js`, `static/js/header.js`.
- **`make check-reqs` fixed:** `uv export` errors are no longer silenced; failures surface cleanly.
- **URLField deprecation warning suppressed:** `RemovedInDjango60Warning` for URLField default scheme filtered via `filterwarnings` in `pyproject.toml` rather than via the deprecated transitional setting.
- **`make check-content` reclassified:** Moved from the CI-safe automated gate to an explicit buyer pre-launch gate in `docs/qa/RELEASE_CHECKLIST.md`. The command requires a populated database and is not CI-safe.
- **Test coverage closed:** View tests added for H-07 (hero placeholder background) and N-01 (logo override suppresses text/monogram). N-06 (transparent home state) signed off via CSS review. G-10 (horizontal overflow) documented as known debt requiring browser render.
- **Privacy policy wording:** Clarified that analytics/error-monitoring services are optional and buyer-enabled.
- **Module docstrings:** "Jeannote" product-name residue replaced with neutral "template repo" language throughout `apps/*/` and `docs/`.

### Known debt — carried forward explicitly

- **G-10 (horizontal overflow):** No automated assertion possible without a browser render viewport. Carry to buyer QA.
- **Branded 404 smoke path:** Dev-server smoke (`DEBUG=True`) cannot prove the custom 404 template. Requires a prod-like instance with `DEBUG=False`.
- **Buyer pre-launch gates:** `make check-content`, `make check-deploy`, and `make smoke-prod` are buyer responsibilities against their customized deployment database; they are outside the template release scope.

---

## [1.0.0] — 2026-03-22

Initial release of the Architecture Portfolio Django Template.

### Included

#### Core platform

- Django 5.2 LTS application with five domain apps: `core`, `pages`, `projects`, `services`, `contact`
- `SiteSettings` and `AboutProfile` singleton models — all public content driven from admin, zero hardcoding
- Seven pages: home, project list, project detail, about, services, contact, contact success
- Full Django admin for all models

#### Projects

- Full project case-study structure: overview, challenge, concept, process, outcome
- Gallery image model (`ProjectImage`) with type classification
- Testimonial model — per-project or site-wide
- Category filter on project list
- Featured flag for homepage display
- Per-project SEO title, meta description, and OG image

#### Contact form

- Submission saved to database on every post — no dependency on email delivery for record-keeping
- Email notification to `CONTACT_EMAIL` on submission
- Honeypot spam field
- Timing-based bot rejection (submission token with minimum age)
- Minimum message length validation
- Email-failure resilience — inquiry saved and user redirected even if SMTP fails

#### Production readiness

- `config.settings.prod` with HSTS, SSL redirect, secure cookies, `DEBUG=False`
- Cloudinary media storage for durable uploads on ephemeral platforms (Railway, Heroku)
- PostgreSQL support via `DATABASE_URL`
- Whitenoise static file serving — no CDN required
- Sentry integration — exception monitoring, opt-in via `SENTRY_DSN`
- Auto-generated XML sitemap for all pages and projects
- GA4 analytics — Measurement ID managed in admin, no code changes

#### Management commands

- `seed_demo` — idempotent starter content for new installs (SiteSettings, AboutProfile, 6 services, 4 projects, 3 testimonials)
- `seed_about` — fills blank AboutProfile fields; `--force` to overwrite
- `seed_services` — fills blank service records; `--reset` to reinitialise all
- `bootstrap_project` — creates a Project record from local files; `--dry-run` required first
- `import_project_images` — attaches gallery images to an existing project; `--dry-run` required first
- `check_content_readiness` — pre-launch audit; exits 1 if required fields are missing or at placeholder values

#### Launch safety

- `check_content_readiness` flags blank and starter/demo content across site settings, About copy, services, projects, and testimonials
- System check `core.W001` — warns in production-like mode if a development email backend is still active
- System check `core.W006` — warns if `CONTACT_EMAIL` is blank

#### Developer tooling

- 100+ automated tests across pytest, pytest-django, and Playwright
- Playwright e2e tests for contact form submission, homepage, navigation, projects, and services
- GitHub Actions CI — lint, type-check, tests, Django system check, migration drift check, deploy check, dependency drift check
- pre-commit hooks (ruff, formatting, common file checks, branch protection)
- Makefile with `health`, `check-deploy`, `smoke`, `coverage`, `reqs`, and `clean-*` targets
- Docker + Compose for local dev without installing Python on the host
- Railway deployment config (`Procfile` + `railway.toml`) ready for first deploy

#### Documentation

- `README.md` — full technical reference and deployment guide
- `SETUP.md` — buyer-facing phase-by-phase guide from fresh clone to live site
- `.env.example` — fully annotated environment configuration template
