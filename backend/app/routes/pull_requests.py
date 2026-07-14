from flask import Blueprint, jsonify, request
from sqlalchemy import or_

from app.extensions import db
from app.models import PullRequest, Repository
from app.services.analysis_service import analyze_and_store


pull_requests_bp = Blueprint("pull_requests", __name__)


def _apply_sort(query, sort_key: str, sort_order: str):
    allowed = {
        "updated_at": PullRequest.updated_at,
        "created_at": PullRequest.created_at,
        "risk_score": PullRequest.risk_score,
        "title": PullRequest.title,
        "number": PullRequest.github_pr_number,
    }
    column = allowed.get(sort_key, PullRequest.updated_at)
    return query.order_by(column.asc() if sort_order == "asc" else column.desc())


@pull_requests_bp.get("/pull-requests")
def list_pull_requests():
    state = request.args.get("state", "all")
    risk = request.args.get("risk", "all")
    search = request.args.get("search", "").strip()
    normalized_search = search[1:] if search.startswith("#") else search
    sort_key = request.args.get("sort", "updated_at")
    sort_order = request.args.get("order", "desc")

    query = PullRequest.query.join(Repository)
    if state != "all":
        query = query.filter(PullRequest.state == state)
    if risk != "all":
        query = query.filter(PullRequest.risk_level == risk)
    if search:
        term = f"%{search}%"
        filters = [
            PullRequest.title.ilike(term),
            PullRequest.author.ilike(term),
            Repository.full_name.ilike(term),
        ]
        if normalized_search.isdigit():
            filters.append(PullRequest.github_pr_number == int(normalized_search))
        query = query.filter(or_(*filters))

    query = _apply_sort(query, sort_key, sort_order)
    items = [pull_request.to_list_dict() for pull_request in query.all()]

    return jsonify(
        {
            "items": items,
            "total": len(items),
            "filters": {
                "state": state,
                "risk": risk,
                "search": search,
                "sort": sort_key,
                "order": sort_order,
            },
        }
    )


@pull_requests_bp.get("/pull-requests/<int:pull_request_id>")
def get_pull_request(pull_request_id: int):
    pull_request = db.get_or_404(PullRequest, pull_request_id)
    return jsonify({"item": pull_request.to_detail_dict()})


@pull_requests_bp.post("/pull-requests/<int:pull_request_id>/analyze")
def analyze_pull_request_route(pull_request_id: int):
    pull_request = db.get_or_404(PullRequest, pull_request_id)
    analysis = analyze_and_store(pull_request)
    db.session.commit()
    return jsonify({"message": "Pull request analyzed successfully.", "analysis": analysis.to_dict()})
