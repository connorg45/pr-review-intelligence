# Contributing

## Development setup

Use Python 3.12 and Node.js 20.19 or newer.

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
cp .env.example .env
pytest -q

cd ../frontend
npm ci
npm test
npm run build
```

Docker provides the closest match to the production runtime:

```bash
docker build -t pr-review-intelligence:test .
```

## Pull requests

- Keep changes focused and preserve existing behavior unless the change explains the intended product impact.
- Add regression tests for bug fixes and meaningful behavior changes.
- Do not weaken tests, dependency audits, read-only hosting defaults, or workflow permissions.
- Never commit `.env` files, credentials, database files, logs, build output, or generated local state.
- Update documentation when commands, configuration, endpoints, or user-visible behavior change.

By contributing, you agree that your contribution is licensed under the MIT License.
