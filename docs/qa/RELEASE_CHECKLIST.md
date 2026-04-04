# Release Checklist

Use this checklist before a tagged release or any buyer-facing delivery. This file is documentation-aware and complements the repo-root [RELEASE.md](../../RELEASE.md).

## 1. Documentation Sync

- [ ] Shared specs match current implementation for any changed global, typography, layout, hero, or navbar behavior.
- [ ] Every changed required state still has a matching row in [TEST_MATRIX.md](TEST_MATRIX.md).
- [ ] Any configurable behavior changed in code is queued for Phase 3 admin docs; do not silently ship undocumented config changes.
- [ ] Known docs debt remains visible if any exists.
  Current status:
  - No unresolved doc-to-implementation drift is currently tracked after the latest sync pass.
  - Open evidence gaps and `Partial` rows remain tracked in `docs/qa/TEST_MATRIX.md` and in spec known-gap sections.

## 2. Automated Gate

- [ ] `make health`
- [ ] `make test-e2e`
- [ ] `make check-content`
  This verifies database-backed launch content and public-facing setup, including the public contact email shown on the site.
- [ ] `make check-deploy`
  This verifies production environment assumptions, including the internal contact-notification inbox `CONTACT_EMAIL`.
- [ ] `make check-reqs`

## 3. State Coverage Review

- [ ] Review all `Partial` and `Gap` rows in [TEST_MATRIX.md](TEST_MATRIX.md) that are touched by this release.
- [ ] If hero behavior changed, run `uv run python scripts/audit_hero_spec.py`.
- [ ] If navbar brand or mobile-menu behavior changed, run `uv run python scripts/audit_nav_brand.py`.
- [ ] If typography fit changed in shared surfaces, run `uv run python scripts/audit_typography_qa.py`.

## 4. Smoke

- [ ] Run `make smoke` against the staging or local verification instance.
  This verifies the rendered public routes and key assets on a running instance; it does not replace `make check-content` or `make check-deploy`.
  Use a prod-like verification instance for this step. A plain `DEBUG=True` dev server will not prove the branded 404 path used in the smoke check.
- [ ] Run `DEPLOY_URL=https://... make smoke-prod` against production when appropriate for the release process.

## 5. Release Notes And Follow-Up

- [ ] Update the repo-root release notes process in [RELEASE.md](../../RELEASE.md) if the release workflow itself changed.
- [ ] Carry forward any unresolved docs/test debt explicitly in the PR or release notes; do not let it disappear from the checklist just because the code shipped.
