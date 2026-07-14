from app.extensions import db


class PullRequest(db.Model):
    __tablename__ = "pull_requests"
    __table_args__ = (db.UniqueConstraint("repository_id", "github_pr_number", name="uq_repo_pr_number"),)

    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey("repositories.id"), nullable=False, index=True)
    github_pr_number = db.Column(db.Integer, nullable=False)
    github_pr_id = db.Column(db.Integer, nullable=True)
    title = db.Column(db.String(500), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(32), nullable=False, default="open")
    url = db.Column(db.String(500), nullable=True)
    additions = db.Column(db.Integer, nullable=False, default=0)
    deletions = db.Column(db.Integer, nullable=False, default=0)
    changed_files_count = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False)
    merged_at = db.Column(db.DateTime(timezone=True), nullable=True)
    first_review_at = db.Column(db.DateTime(timezone=True), nullable=True)
    risk_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(32), nullable=True)
    analysis_status = db.Column(db.String(32), nullable=False, default="pending")
    last_synced_at = db.Column(db.DateTime(timezone=True), nullable=True)

    repository = db.relationship("Repository", back_populates="pull_requests")
    files = db.relationship(
        "PullRequestFile",
        back_populates="pull_request",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="PullRequestFile.path",
    )
    analysis_results = db.relationship(
        "AnalysisResult",
        back_populates="pull_request",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="desc(AnalysisResult.analyzed_at)",
    )
    event_logs = db.relationship(
        "EventLog",
        back_populates="pull_request",
        lazy="selectin",
        order_by="desc(EventLog.created_at)",
    )

    @property
    def latest_analysis(self):
        return self.analysis_results[0] if self.analysis_results else None

    def to_list_dict(self) -> dict:
        latest = self.latest_analysis
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "repository_name": self.repository.full_name if self.repository else None,
            "github_pr_number": self.github_pr_number,
            "github_pr_id": self.github_pr_id,
            "title": self.title,
            "author": self.author,
            "state": self.state,
            "url": self.url,
            "additions": self.additions,
            "deletions": self.deletions,
            "changed_files_count": self.changed_files_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "merged_at": self.merged_at.isoformat() if self.merged_at else None,
            "first_review_at": self.first_review_at.isoformat() if self.first_review_at else None,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "analysis_status": self.analysis_status,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "risk_reasons_preview": latest.reasons_json[:2] if latest else [],
        }

    def to_detail_dict(self) -> dict:
        latest = self.latest_analysis
        return {
            **self.to_list_dict(),
            "analysis_result": latest.to_dict() if latest else None,
            "files": [file.to_dict() for file in self.files],
            "analysis_history": [result.to_dict() for result in self.analysis_results],
            "activity": [event.to_dict() for event in self.event_logs],
        }
