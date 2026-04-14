# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# LOCAL DEVELOPMENT ONLY — do not use this image for production.
#
# Production deployment: Railway reads Procfile + railway.toml directly.
# This Dockerfile exists solely to give a reproducible local environment
# without installing Python or uv on the host machine.
#
# Because this image never runs in production, Docker security best-practices
# that only apply to production images (HEALTHCHECK, non-root USER) are
# intentionally omitted. The suppressions below are honest, not lazy.
# checkov:skip=CKV_DOCKER_2:dev-only image, HEALTHCHECK not needed
# checkov:skip=CKV_DOCKER_3:dev-only image, non-root user not required
# checkov:skip=CKV2_DOCKER_3:dev-only image, non-root user not required
# ---------------------------------------------------------------------------

FROM python:3.13-slim

# Prevent .pyc files and buffer stdout/stderr so logs appear immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv — the package manager used by this project
RUN pip install --no-cache-dir uv

# ---------------------------------------------------------------------------
# Layer: dependencies
# Copy only the dependency files first so Docker can cache this step
# independently of source code changes.
# ---------------------------------------------------------------------------
COPY pyproject.toml uv.lock ./

# Install all dependencies (runtime + dev) into /opt/venv so that the bind-mount
# at /app (used in compose for live reloading) does not shadow the virtualenv.
# UV_PROJECT_ENVIRONMENT   — tells uv sync where to create/use the virtualenv
# VIRTUAL_ENV              — tells standard Python tools the venv is active
ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    VIRTUAL_ENV=/opt/venv
RUN uv sync --frozen --group dev

# Activate the virtualenv for all subsequent RUN/CMD instructions
ENV PATH="/opt/venv/bin:$PATH"

# ---------------------------------------------------------------------------
# Layer: application source
# ---------------------------------------------------------------------------
COPY . .

EXPOSE 8000

# Default command: Django dev server, listening on all interfaces.
# compose.yml overrides this to run migrations first.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
