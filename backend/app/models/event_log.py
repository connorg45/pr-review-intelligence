from datetime import datetime, timezone

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class EventLog(db.Model):
    __tablename__ = "event_logs"

    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey("repositories.id"), nullable=True, index=True)
    pull_request_id = db.Column(db.Integer, db.ForeignKey("pull_requests.id"), nullable=True, index=True)
    event_type = db.Column(db.String(64), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    repository = db.relationship("Repository", back_populates="event_logs")
    pull_request = db.relationship("PullRequest", back_populates="event_logs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "repository_name": self.repository.full_name if self.repository else None,
            "pull_request_id": self.pull_request_id,
            "pull_request_number": self.pull_request.github_pr_number if self.pull_request else None,
            "event_type": self.event_type,
            "message": self.message,
            "metadata": self.metadata_json,
            "created_at": self.created_at.isoformat(),
        }
