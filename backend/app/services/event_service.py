from app.extensions import db
from app.models import EventLog


def log_event(
    *,
    event_type: str,
    message: str,
    repository_id: int | None = None,
    pull_request_id: int | None = None,
    metadata: dict | None = None,
) -> EventLog:
    event = EventLog(
        repository_id=repository_id,
        pull_request_id=pull_request_id,
        event_type=event_type,
        message=message,
        metadata_json=metadata or {},
    )
    db.session.add(event)
    return event
