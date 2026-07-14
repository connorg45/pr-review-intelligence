from datetime import datetime, timezone

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SyncRun(db.Model):
    __tablename__ = "sync_runs"

    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey("repositories.id"), nullable=False, index=True)
    source_type = db.Column(db.String(32), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="running")
    started_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    pr_count = db.Column(db.Integer, nullable=False, default=0)
    metadata_json = db.Column(db.JSON, nullable=False, default=dict)
    error_message = db.Column(db.Text, nullable=True)

    repository = db.relationship("Repository", back_populates="sync_runs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "repository_name": self.repository.full_name if self.repository else None,
            "source_type": self.source_type,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "pr_count": self.pr_count,
            "metadata": self.metadata_json,
            "error_message": self.error_message,
        }
