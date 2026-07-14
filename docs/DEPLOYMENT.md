# Deployment

## Render Blueprint

The repository includes a Docker deployment blueprint, a health check, and a managed PostgreSQL connection.

1. Open the Render deploy link in the main README.
2. Connect the repository and approve the web service and database.
3. Wait for the Docker build and `/api/health` check to pass.
4. Confirm `WRITE_OPERATIONS_ENABLED` remains `false` for a public deployment.

The hosted application loads sample data without credentials. Repository sync, sample reset, and persisted re-analysis are disabled by default.

Do not add `GITHUB_TOKEN` to a public deployment. The application is single-user and does not provide the authentication or tenant isolation required to protect token-visible repository data.

## Trusted Docker host

Build and start the production image:

```bash
docker build -t pr-review-intelligence .
docker run --rm -p 8000:8000 \
  -e SECRET_KEY=replace-with-a-random-secret \
  -e DATABASE_URL=sqlite:////data/pr_review_intelligence.db \
  -e WRITE_OPERATIONS_ENABLED=true \
  -v pr-review-data:/data \
  pr-review-intelligence
```

Enable write operations only when the service is restricted to trusted users or a private network. Add a fine-grained `GITHUB_TOKEN` only when live sync is required.

## Docker Compose

```bash
docker compose up --build
```

Compose stores SQLite data in the `pr-data` volume and enables writes for local use. Set `GITHUB_TOKEN` in the shell before starting Compose if live sync is needed.

## Configuration

| Variable | Purpose | Default |
| --- | --- | --- |
| `SECRET_KEY` | Application signing secret | Development fallback; set in production |
| `DATABASE_URL` | SQLite or PostgreSQL connection URL | Local SQLite |
| `GITHUB_TOKEN` | Optional read-only token for trusted live sync | Empty |
| `WRITE_OPERATIONS_ENABLED` | Allows sync, reset, and re-analysis HTTP requests | `false` |
| `AUTO_SEED_DEMO` | Seeds sample data when the database is empty | `true` |
| `TRUSTED_HOSTS` | Comma-separated allowed HTTP hosts | Render hostname when available |

Never commit `.env` files or access tokens.
