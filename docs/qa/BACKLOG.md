# Post-Release Backlog

Items deferred from the v1.0.1 lock-ready pass, plus items identified during the
v1.0.2 buyer-readiness drill (2026-04-12). Items are tagged with their target
release: `[1.0.2]` or `[later]`.

Each item records its origin, why it was deferred, and what would close it.

---

## Adoption friction — v1.0.2 targets

These were found during the fresh-install drill (2026-04-12): clone → install →
configure → migrate → seed → run, executed as a buyer with no prior context.

### B-06 — Secret key generation command fails without active venv `[1.0.2]`

**Origin:** Fresh-install drill 2026-04-12.
**Issue:** SETUP.md, DEMO.md, README.md, `.env.example`, and `docs/recovery-runbook.md`
all instructed buyers to run:
```
python -c "from django.core.management.utils import get_random_secret_key; ..."
```
This fails with `ModuleNotFoundError: No module named 'django'` on any machine
where Django is not installed globally (the common case after `uv sync`).
**Fix applied:** All occurrences updated to `uv run python -c "..."` (2026-04-12).
**Status:** Closed — fixed in-place across all five files.

---

### B-07 — `seed_demo` labelled "optional" but site is blank without it `[1.0.2]`

**Origin:** Fresh-install drill 2026-04-12.
**Issue:** README.md Step 5 header read "Seed starter/demo content (optional)".
A buyer who skips it lands on a blank site with no projects, no About content,
and no services rendering. "Optional" was technically accurate (the site starts)
but practically misleading for anyone evaluating the template.
**Fix applied:** Label changed to "(recommended for first run)" with an explicit
"Without this step the site will be mostly blank" callout (2026-04-12).
**Status:** Closed — fixed in README.md.

---

### B-08 — No "expected behaviour" framing for `check_content_readiness` after seed `[1.0.2]`

**Origin:** Fresh-install drill 2026-04-12.
**Issue:** Running `make check-content` immediately after `seed_demo` shows 9 blockers
and 5 warnings, all expected and correct. No text in Phase 1 warns the buyer that
this output is normal — a buyer may interpret it as something broken.
**Fix applied:** Callout note added after the `seed_demo` paragraph in SETUP.md Phase 1
(2026-04-12).
**Status:** Closed — fixed in SETUP.md.

---

## Template QA debt

### B-01 — Horizontal overflow at baseline viewports (G-10)

**Origin:** Pre-existing gap since the 2026-03-31 doc-to-implementation sync audit.
**Deferred because:** Horizontal-overflow detection requires a rendered browser viewport. There is no automated assertion path available from CSS source or view tests alone.
**Matrix row:** `G-10` — status `Known debt`.
**Closes when:** A browser e2e assertion or manual QA pass confirms no horizontal overflow at `320px`, `390px`, `768px`, and `1280px` against the shipped CSS.
**Target:** `[later]`

---

### B-02 — Branded 404 smoke path (prod-like instance)

**Origin:** Confirmed limitation during the v1.0.1 smoke run (2026-04-12).
**Deferred because:** Django's dev server (`DEBUG=True`) serves the technical 404 page rather than the custom `404.html` template. The smoke script's post-deploy branded-404 check always fails against a dev-server target.
**Closes when:** `make smoke` (or `make smoke-prod`) is run against a prod-like instance with `DEBUG=False` where the custom template is served.
**Target:** `[later]`

---

## Buyer pre-launch scope (not template release scope)

These items are not tracked as template debt — they are buyer responsibilities. They are listed here so the distinction between template release scope and buyer launch scope is explicit.

### B-03 — `make check-content` against buyer's database

**Why it is buyer scope:** This command requires a populated database with real content (projects, site settings, contact config). The template ships with starter/demo content for evaluation. Requiring the template database to look launch-ready would confuse template release proof with buyer launch proof.
**Buyer action:** Run `make check-content` against the customized deployment database before any real site goes live.

### B-04 — `make check-deploy` against buyer's production environment

**Why it is buyer scope:** Verifies production environment assumptions (`ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, SMTP, Cloudinary, Sentry, `CONTACT_EMAIL`). These are buyer-configured values; they cannot be verified from the template repository.
**Buyer action:** Run `make check-deploy` with production env vars set.

### B-05 — `make smoke-prod` against buyer's deployed URL

**Why it is buyer scope:** End-to-end live-route verification against the buyer's actual domain, including the branded 404 path.
**Buyer action:** Run `DEPLOY_URL=https://your-domain.com make smoke-prod` after deployment.

---

## Conventions

- Do not close items in this file by editing them out. Mark them `Closed — <date>` and record the evidence.
- Do not add new items here as a way to defer work that should be in the release. Items belong here only when they are explicitly signed off as deferred at a release boundary.
- Template debt items should be promoted to `docs/qa/TEST_MATRIX.md` rows when closed.
