# Performance measurements

## Method

`backend/scripts/benchmark.py` creates the Flask application with an in-memory SQLite database and the seven-PR sample dataset. It warms each endpoint with 10 requests, then records 250 sequential requests through Flask's test client using `time.perf_counter()`.

The measurement isolates application and database work. It does not include internet latency, TLS, a reverse proxy, browser rendering, or concurrent load.

## Results

Measured on July 9, 2026 with Python 3.12:

| Endpoint | Requests | Median | p95 | Maximum |
| --- | ---: | ---: | ---: | ---: |
| `/api/health` | 250 | 0.24 ms | 0.29 ms | 1.37 ms |
| `/api/dashboard/summary` | 250 | 4.84 ms | 6.43 ms | 35.86 ms |
| `/api/pull-requests` | 250 | 3.72 ms | 3.89 ms | 27.24 ms |
| `/api/events?limit=100` | 250 | 3.88 ms | 4.36 ms | 26.63 ms |

## Reproduce

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.benchmark --iterations 250
```

Results will vary by hardware, database engine, dataset size, and background load. Hosted performance should be measured separately over HTTP with production data before making capacity claims.
