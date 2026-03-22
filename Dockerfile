# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Local development Dockerfile — NOT for production deployment.
# Production is handled by Railway via Procfile + railway.toml.
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
