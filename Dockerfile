# HR Properties Backend — Django + DRF + Gunicorn
# Python 3.11-slim: matches GitHub Actions python-version (deploy.yml:20).
# Slim (not alpine) because psycopg2-binary needs glibc.
FROM python:3.11-slim AS runtime

# System deps: libpq5 for psycopg2 runtime, curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create non-root user
RUN groupadd -r app && useradd -r -g app -u 1001 app

# Copy dependency manifest first for layer caching
COPY --chown=app:app requirements.txt ./

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY --chown=app:app . .

# Create directories for static files and media (mounted as volumes in compose)
RUN mkdir -p /app/staticfiles /app/media && chown app:app /app/staticfiles /app/media

USER 1001:1001

EXPOSE 8000

# No /health endpoint found in urls.py — use TCP check on port 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://127.0.0.1:8000/admin/ || exit 1

# Migrate + collectstatic + start gunicorn.
# exec ensures gunicorn becomes PID 1 and receives SIGTERM for graceful shutdown.
# gunicorn.conf.py provides: 2 workers, gthread, 2 threads, 120s timeout.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn --bind 0.0.0.0:8000 --config gunicorn.conf.py hr_properties.wsgi:application"]