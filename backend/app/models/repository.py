from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Repository(db.Model):
    __tablename__ = "repositories"
    __table_args__ = (UniqueConstraint("owner", "name", name="uq_repository_owner_name"),)

    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String(120), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(255), nullable=False, unique=True)
    source_type = db.Column(db.String(32), nullable=False, default="demo")
    github_repo_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    pull_requests = db.relationship(
        "PullRequest",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sync_runs = db.relationship(
        "SyncRun",
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(SyncRun.started_at)",
    )
    event_logs = db.relationship(
        "EventLog",
        back_populates="repository",
        lazy="selectin",
        order_by="desc(EventLog.created_at)",
    )

    def to_dict(self) -> dict:
        open_prs = [pr for pr in self.pull_requests if pr.state == "open"]
        analyzed = [pr for pr in self.pull_requests if pr.risk_score is not None]
        high_risk = [pr for pr in self.pull_requests if pr.risk_level == "high"]
        average_risk = round(sum(pr.risk_score for pr in analyzed) / len(analyzed), 1) if analyzed else 0

        return {
            "id": self.id,
            "owner": self.owner,
            "name": self.name,
            "full_name": self.full_name,
            "source_type": self.source_type,
            "github_repo_id": self.github_repo_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "stats": {
                "total_prs": len(self.pull_requests),
                "open_prs": len(open_prs),
                "high_risk_prs": len(high_risk),
                "average_risk_score": average_risk,
            },
        }
