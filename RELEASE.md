# Release Process

Use this checklist when cutting a tagged product release.

## 1. Prepare the release

1. Start from a clean `main` working tree.
2. Update the version in [pyproject.toml](pyproject.toml).
3. Add or update the top entry in [CHANGELOG.md](CHANGELOG.md).
4. Update the version/status block in [README.md](README.md).
5. If the commercial terms changed, update the version line in [LICENSE.md](LICENSE.md).

## 2. Run the release checks

**Dependency source of truth:** `pyproject.toml` + `uv.lock` own the dependency graph.
`requirements.txt` is a generated compatibility artifact only — export it with `uv export`, never edit it by hand.

Run the full release checks before tagging:

- `make check-content` verifies launch content and public-facing setup from the database, including public contact details such as `Site Settings.contact_email`.
- `make check-deploy` verifies production environment assumptions such as `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, SMTP settings, Cloudinary credentials, Sentry, and the internal contact-notification inbox `CONTACT_EMAIL`.
- `make smoke` and `make smoke-prod` verify the live rendered routes and deployment reachability; they do not replace the content or deploy checks.

Run the repo checks:

```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
uv run pytest tests/e2e --override-ini="addopts=-v --tb=short" -m e2e --browser chromium -q
make check-content
make check-deploy
make check-reqs
```

Then verify a running instance:

```bash
make smoke
DEPLOY_URL=https://your-domain.com make smoke-prod
```

Use `make smoke` against staging or another prod-like verification instance. A plain local dev server running with `DEBUG=True` will not prove the branded 404 path used in the smoke check.

## 3. Commit and tag

```bash
git add -A
git commit -m "chore: release v1.0.0"
git tag -a v1.0.0 -m "Release v1.0.0"
```

Push the release commit and tag:

```bash
git push origin main
git push origin v1.0.0
```

## 4. Buyer guidance

- Treat tagged releases as the stable install target.
- Tell buyers to pin a release tag or release archive, not `main`.
- Use the matching [CHANGELOG.md](CHANGELOG.md) entry as the release notes.
