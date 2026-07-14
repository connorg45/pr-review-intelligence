from app.extensions import db


class PullRequestFile(db.Model):
    __tablename__ = "pull_request_files"

    id = db.Column(db.Integer, primary_key=True)
    pull_request_id = db.Column(db.Integer, db.ForeignKey("pull_requests.id"), nullable=False, index=True)
    path = db.Column(db.String(500), nullable=False)
    additions = db.Column(db.Integer, nullable=False, default=0)
    deletions = db.Column(db.Integer, nullable=False, default=0)
    change_type = db.Column(db.String(32), nullable=False, default="modified")
    is_sensitive = db.Column(db.Boolean, nullable=False, default=False)
    is_test_file = db.Column(db.Boolean, nullable=False, default=False)

    pull_request = db.relationship("PullRequest", back_populates="files")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "path": self.path,
            "additions": self.additions,
            "deletions": self.deletions,
            "change_type": self.change_type,
            "is_sensitive": self.is_sensitive,
            "is_test_file": self.is_test_file,
        }
