from datetime import datetime, timezone

from app.extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class AnalysisResult(db.Model):
    __tablename__ = "analysis_results"

    id = db.Column(db.Integer, primary_key=True)
    pull_request_id = db.Column(db.Integer, db.ForeignKey("pull_requests.id"), nullable=False, index=True)
    engine_version = db.Column(db.String(32), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(32), nullable=False)
    reasons_json = db.Column(db.JSON, nullable=False, default=list)
    reviewer_recommendations_json = db.Column(db.JSON, nullable=False, default=list)
    analyzed_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    pull_request = db.relationship("PullRequest", back_populates="analysis_results")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "engine_version": self.engine_version,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "reasons": self.reasons_json,
            "reviewer_recommendations": self.reviewer_recommendations_json,
            "analyzed_at": self.analyzed_at.isoformat(),
        }
