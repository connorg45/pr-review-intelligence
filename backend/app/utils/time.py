from datetime import datetime, timezone


def parse_github_datetime(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def as_utc(value: datetime | None) -> datetime | None:
    """Return a timezone-aware UTC datetime, including for SQLite values."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def datetimes_equal(left: datetime | None, right: datetime | None) -> bool:
    return as_utc(left) == as_utc(right)
