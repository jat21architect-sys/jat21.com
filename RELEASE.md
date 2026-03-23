# Release Process

Use this checklist when cutting a tagged product release.

## 1. Prepare the release

1. Start from a clean `main` working tree.
2. Update the version in [pyproject.toml](pyproject.toml).
3. Add or update the top entry in [CHANGELOG.md](CHANGELOG.md).
4. Update the version/status block in [README.md](README.md).
5. If the commercial terms changed, update the version line in [LICENSE.md](LICENSE.md).

## 2. Run the release checks

Run the full repo checks before tagging:

```bash
uv run ruff check .
uv run mypy .
uv run pytest -q
uv run pytest tests/e2e --override-ini="addopts=-v --tb=short" -m e2e --browser chromium -q
make check-deploy
make check-reqs
```

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
