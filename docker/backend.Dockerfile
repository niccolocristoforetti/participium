# Backend image - Flask development server.
# Build context: repository root. Every COPY path is relative to that context,
# NOT to this Dockerfile's directory (docker/).
FROM python:3.12-slim

WORKDIR /usr/src/app

# Install Python dependencies first so this layer is cached across source changes.
COPY src/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend source from the build context.
# Local .env, virtualenvs, caches and instance files are excluded via .dockerignore.
COPY src/backend/ ./

# Container port (documentation only; the host mapping is set in docker-compose.yml).
EXPOSE 5050

# Development entry point. --without-threads serializes requests so the single
# process-level SQLAlchemy connection is never shared across threads.
CMD ["flask", "--app", "wsgi:app", "run", "--host", "0.0.0.0", "--port", "5050", "--without-threads"]
