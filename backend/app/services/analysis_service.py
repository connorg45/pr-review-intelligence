from datetime import datetime, timezone

from app.extensions import db
from app.models import AnalysisResult, PullRequest
from app.services.event_service import log_event
from app.services.reviewer_service import recommend_reviewers
from app.services.risk_engine import analyze_pull_request


def build_snapshot(pull_request: PullRequest) -> dict:
    return {
        "additions": pull_request.additions,
        "deletions": pull_request.deletions,
        "changed_files_count": pull_request.changed_files_count,
        "state": pull_request.state,
        "created_at": pull_request.created_at,
        "files": [file.to_dict() for file in pull_request.files],
    }


def analyze_and_store(pull_request: PullRequest, analyzed_at: datetime | None = None) -> AnalysisResult:
    snapshot = build_snapshot(pull_request)
    risk_result = analyze_pull_request(snapshot)
    reviewer_recommendations = recommend_reviewers(pull_request)
    analysis_time = analyzed_at or datetime.now(timezone.utc)

    analysis = AnalysisResult(
        pull_request_id=pull_request.id,
        engine_version=risk_result["engine_version"],
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"],
        reasons_json=risk_result["reasons"],
        reviewer_recommendations_json=reviewer_recommendations,
        analyzed_at=analysis_time,
    )
    db.session.add(analysis)

    pull_request.risk_score = risk_result["risk_score"]
    pull_request.risk_level = risk_result["risk_level"]
    pull_request.analysis_status = "completed"

    event = log_event(
        event_type="analysis.completed",
        message=f"Risk score updated for PR #{pull_request.github_pr_number}: {pull_request.risk_level} risk.",
        repository_id=pull_request.repository_id,
        pull_request_id=pull_request.id,
        metadata={
            "risk_score": pull_request.risk_score,
            "risk_level": pull_request.risk_level,
            "engine_version": analysis.engine_version,
        },
    )
    event.created_at = analysis_time

    db.session.flush()
    return analysis
