from __future__ import annotations

import argparse
import json
import statistics
import time

from app import create_app
from app.config import TestingConfig


class BenchmarkConfig(TestingConfig):
    AUTO_SEED_DEMO = True


def percentile(values: list[float], percent: float) -> float:
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * percent), len(ordered) - 1)
    return ordered[index]


def measure(client, path: str, iterations: int) -> dict:
    for _ in range(10):
        response = client.get(path)
        if response.status_code != 200:
            raise RuntimeError(f"Warmup request failed for {path}: {response.status_code}")

    durations = []
    for _ in range(iterations):
        started = time.perf_counter()
        response = client.get(path)
        durations.append((time.perf_counter() - started) * 1000)
        if response.status_code != 200:
            raise RuntimeError(f"Benchmark request failed for {path}: {response.status_code}")

    return {
        "path": path,
        "requests": iterations,
        "median_ms": round(statistics.median(durations), 2),
        "p95_ms": round(percentile(durations, 0.95), 2),
        "max_ms": round(max(durations), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure local API response latency with the sample dataset.")
    parser.add_argument("--iterations", type=int, default=250)
    args = parser.parse_args()
    if args.iterations < 1:
        parser.error("iterations must be at least 1")

    app = create_app(BenchmarkConfig)
    client = app.test_client()
    endpoints = [
        "/api/health",
        "/api/dashboard/summary",
        "/api/pull-requests",
        "/api/events?limit=100",
    ]
    results = [measure(client, path, args.iterations) for path in endpoints]
    print(json.dumps({"iterations_per_endpoint": args.iterations, "results": results}, indent=2))


if __name__ == "__main__":
    main()
