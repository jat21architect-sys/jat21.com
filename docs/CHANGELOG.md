# Changelog

All notable changes to this documentation system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- The repo-root `README.md` homepage descriptions now match the current shipped homepage implementation.
- Legacy operational docs are explicitly linked from `docs/README.md` and intentionally kept outside the locked structure for now.
- The repo now separates responsibilities more explicitly inside `apps/`: `apps/core` holds cross-cutting Django glue, `apps/site` holds site-wide content/config/admin behavior, `apps/pages` holds public page composition, the shared shell remains repo-level in `templates/` and `static/`, and domain apps own their route CSS in app-local static folders.
- `Site Settings` admin now surfaces launch-readiness blockers and warnings, and buyer-facing admin guidance is sharper around brand fallback, public contact setup, and homepage-driving project choices.
- The contact flow now distinguishes notification success from saved-only fallback states, uses calmer invalid-submission recovery copy, and surfaces missing internal notification setup through launch readiness and admin warnings.
- Project detail pages now resolve hero/share media through one `cover_image → first gallery image` fallback path, use a truthful supporting-media label, and pass the project category into the contact-form prefill CTA.
- Public image markup now emits real intrinsic dimensions when valid metadata is available, hero images use `fetchpriority="high"`, and buyer-facing admin guidance is clearer about upload-optimized cover, gallery, and share images.
- Release instructions now distinguish content readiness, deploy/environment readiness, and live smoke verification, and the deterministic smoke baseline now includes the public privacy route.
- Shared-template analytics behavior is now covered explicitly: the GA script is absent when `google_analytics_id` is blank and present only when it is configured.
- Ruff and mypy release gates now intentionally exclude ad hoc audit, screenshot, and scratch helper scripts while keeping app code, tests, and the smoke check in scope.
- Release docs now state that `make smoke` should target a prod-like verification instance; a plain `DEBUG=True` dev server does not prove the branded 404 path.

## [0.1.0] - 2026-03-30

### Added

- A documentation-system landing page with contribution rules, stale-doc policy, the golden rules, and the locked file map.
- Shared specs for global behavior, typography, and layout grounded in the current templates, CSS, JS, and tests.
- A gateway technical spec plus measurable component specs for the homepage hero and shared navbar.
- QA docs covering testing policy, state coverage, and release gating.
- Product doctrine, admin field reference, buyer-oriented customization guidance, and a reverse-chronological decision log.
