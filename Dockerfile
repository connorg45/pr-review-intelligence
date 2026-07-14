FROM node:20-alpine@sha256:fb4cd12c85ee03686f6af5362a0b0d56d50c58a04632e6c0fb8363f609372293 AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim@sha256:64695412729fbe8cf054511723820c82bbe5a077d4a6b4070cd4a7225d3422ce AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app
COPY backend/requirements.lock backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock

COPY backend/ backend/
COPY --from=frontend-build /app/frontend/dist frontend/dist

RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /data && chown -R app:app /app /data
USER app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.getenv('PORT', '8000') + '/api/health', timeout=3)"

CMD ["sh", "-c", "gunicorn --chdir backend --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads 4 --timeout 60 run:app"]
