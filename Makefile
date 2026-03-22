.PHONY: tree run migrate migrations superuser seed collectstatic \
        lint fmt typecheck test health smoke smoke-prod check-deploy \
        reqs check-reqs \
        docker-up docker-down docker-test \
        clean clean-pyc clean-static clean-test clean-media clean-db clean-all

SMOKE_BASE_URL ?= http://127.0.0.1:8000

# Print repository tree (excludes venv, caches, build artefacts)
tree:
	@python scripts/tree.py .

# Development server
run:
	uv run python manage.py runserver

# Apply migrations
migrate:
	uv run python manage.py migrate

# Create new migrations
migrations:
	uv run python manage.py makemigrations

# Create superuser
superuser:
	uv run python manage.py createsuperuser

# Seed demo content
seed:
	uv run python manage.py seed_demo

# Collect static files
collectstatic:
	uv run python manage.py collectstatic --noinput

# ---------------------------------------------------------------------------
# Docker — local development only (not Railway deployment)
# ---------------------------------------------------------------------------

# Build image and start the dev server (runs migrate automatically)
docker-up:
	docker compose up --build

# Stop and remove containers
docker-down:
	docker compose down

# Run the test suite inside the running container
docker-test:
	docker compose exec web pytest

# ---------------------------------------------------------------------------
# Dependency management
# ---------------------------------------------------------------------------

# Regenerate requirements.txt from pyproject.toml (used by Railway/nixpacks).
# Run this after any change to [project].dependencies in pyproject.toml.
reqs:
	uv export --no-dev --no-hashes -o requirements.txt

# Check that requirements.txt is in sync with pyproject.toml / uv.lock.
# Exits non-zero if requirements.txt would change — use in CI to catch drift.
check-reqs:
	@uv export --no-dev --no-hashes 2>/dev/null | grep -v '^#' > /tmp/_reqs_fresh.txt; \
	grep -v '^#' requirements.txt > /tmp/_reqs_committed.txt; \
	diff /tmp/_reqs_fresh.txt /tmp/_reqs_committed.txt > /dev/null \
		&& echo "requirements.txt is up to date" \
		|| (echo "ERROR: requirements.txt is out of sync. Run: make reqs" && exit 1)

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------

# Lint (check only)
lint:
	uv run ruff check .

# Lint + auto-fix, then format
fmt:
	uv run ruff check . --fix
	uv run ruff format .

# Type checking
typecheck:
	uv run mypy .

# Run test suite
test:
	uv run pytest

# Run the standard repo health gate used before commits / in CI.
health:
	uv run ruff check .
	uv run mypy .
	uv run pytest
	uv run python manage.py check
	uv run python manage.py makemigrations --check --dry-run
	$(MAKE) check-reqs

# Run test suite with coverage report
coverage:
	uv run pytest --cov --cov-report=term-missing

# Smoke-check a running instance (local dev server or deployed URL).
smoke:
	uv run python scripts/smoke_check.py --base-url "$(SMOKE_BASE_URL)"

# Smoke-check the live production URL.
# Usage: DEPLOY_URL=https://your-domain.com make smoke-prod
# Requires DEPLOY_URL to be set in the environment (or as a Make variable).
smoke-prod:
	@test -n "$(DEPLOY_URL)" || (echo "ERROR: DEPLOY_URL is not set. Usage: DEPLOY_URL=https://... make smoke-prod" && exit 1)
	uv run python scripts/smoke_check.py --base-url "$(DEPLOY_URL)"

# Django deployment security check — always runs against production settings.
# Uses explicit dummy values for all production-only env vars so the check can
# pass cleanly and only fail on real misconfigurations in prod.py or custom checks.
check-deploy:
	@echo "Running manage.py check --deploy against config.settings.prod..."
	DJANGO_SETTINGS_MODULE=config.settings.prod \
	  SECRET_KEY=deploy-check-secret-ThisIsLongEnough1234567890!@#ABCDEF \
	  ALLOWED_HOSTS=example.com \
	  CSRF_TRUSTED_ORIGINS=https://example.com \
	  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
	  EMAIL_HOST=smtp.example.com \
	  EMAIL_PORT=587 \
	  EMAIL_USE_TLS=True \
	  EMAIL_HOST_USER=dummy-user \
	  EMAIL_HOST_PASSWORD=dummy-password \
	  CLOUDINARY_CLOUD_NAME=dummy-cloud \
	  CLOUDINARY_API_KEY=dummy-key \
	  CLOUDINARY_API_SECRET=dummy-secret \
	  SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0 \
	  SENTRY_ENVIRONMENT=production \
	  uv run python manage.py check --deploy

# ---------------------------------------------------------------------------
# Clean targets
# ---------------------------------------------------------------------------

# Remove Python bytecode and cache artefacts
clean-pyc:
	@echo "Removing Python bytecode and caches..."
	@find . -path ./.venv -prune -o -type f -name "*.pyc" -delete -print
	@find . -path ./.venv -prune -o -type f -name "*.pyo" -delete -print
	@find . -path ./.venv -prune -o -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -path ./.venv -prune -o -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "Done."

# Remove pytest / coverage artefacts
clean-test:
	@echo "Removing test, type-check and linter caches..."
	@rm -rf .pytest_cache/ htmlcov/ .coverage coverage.xml .mypy_cache/ .ruff_cache/
	@echo "Done."

# Remove collected static files
clean-static:
	@echo "Removing collected static files (staticfiles/)..."
	@rm -rf staticfiles/
	@echo "Done."

# Remove uploaded media files (prompts for confirmation)
clean-media:
	@echo "WARNING: This will delete all uploaded media files in media/."
	@printf "Are you sure? [y/N] " && read ans && [ "$${ans:-N}" = "y" ]
	@rm -rf media/
	@echo "Done."

# Remove the dev SQLite database (prompts for confirmation)
clean-db:
	@echo "WARNING: This will delete db.sqlite3 and all its data."
	@printf "Are you sure? [y/N] " && read ans && [ "$${ans:-N}" = "y" ]
	@rm -f db.sqlite3
	@echo "Done."

# Safe clean: bytecode + test artefacts + static (no data loss)
clean: clean-pyc clean-test clean-static
	@echo "Workspace clean."

# Nuclear clean: everything including database and media (asks twice)
clean-all: clean-pyc clean-test clean-static
	@echo "WARNING: clean-all will also delete db.sqlite3 and media/."
	@printf "Proceed? [y/N] " && read ans && [ "$${ans:-N}" = "y" ]
	@rm -rf media/ db.sqlite3
	@echo "Full clean complete."
