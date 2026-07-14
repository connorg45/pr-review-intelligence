from pathlib import PurePosixPath


SENSITIVE_KEYWORDS = {
    "auth",
    "permission",
    "security",
    "payments",
    "billing",
    "database",
    "db",
    "migration",
    "migrations",
    "infra",
    "terraform",
    "ci",
    "workflow",
    "config",
    "secrets",
    "roles",
    "policy",
}

CONFIG_PATTERNS = {
    ".github/workflows/",
    "docker-compose",
    "dockerfile",
    "pyproject.toml",
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "requirements.txt",
    ".env",
    "alembic",
}


def normalize_path(path: str) -> str:
    return str(PurePosixPath(path)).lower()


def is_test_file(path: str) -> bool:
    normalized = normalize_path(path)
    name = PurePosixPath(normalized).name
    return (
        "/tests/" in normalized
        or normalized.startswith("tests/")
        or normalized.endswith("_test.py")
        or normalized.endswith(".spec.ts")
        or normalized.endswith(".spec.tsx")
        or normalized.endswith(".test.ts")
        or normalized.endswith(".test.tsx")
        or name.startswith("test_")
    )


def is_sensitive_path(path: str) -> bool:
    normalized = normalize_path(path)
    if any(pattern in normalized for pattern in CONFIG_PATTERNS):
        return True
    return any(keyword in normalized.split("/") for keyword in SENSITIVE_KEYWORDS)


def classify_area(path: str) -> str:
    normalized = normalize_path(path)
    parts = [part for part in normalized.split("/") if part]
    if not parts:
        return "root"
    if parts[0] in {"frontend", "backend", "src", "app"} and len(parts) > 1:
        return "/".join(parts[:2])
    return "/".join(parts[:2]) if len(parts) > 1 else parts[0]
