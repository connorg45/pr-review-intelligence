from collections import defaultdict

from app.models import PullRequest
from app.utils.file_flags import classify_area
from app.utils.time import as_utc


def recommend_reviewers(pull_request: PullRequest, limit: int = 3) -> list[dict]:
    repo = pull_request.repository
    current_author = pull_request.author
    target_areas = {classify_area(file.path) for file in pull_request.files}
    candidates: dict[str, dict] = defaultdict(lambda: {"score": 0, "areas": set(), "pr_count": 0, "recent_prs": 0})

    for historical_pr in repo.pull_requests:
        if historical_pr.id == pull_request.id:
            continue
        if historical_pr.author == current_author:
            continue
        if historical_pr.state not in {"closed", "merged"} and historical_pr.merged_at is None:
            continue

        candidate = candidates[historical_pr.author]
        candidate["pr_count"] += 1
        candidate["score"] += 2
        if (as_utc(pull_request.updated_at) - as_utc(historical_pr.updated_at)).days <= 30:
            candidate["recent_prs"] += 1
            candidate["score"] += 1

        historical_areas = {classify_area(file.path) for file in historical_pr.files}
        overlap = target_areas.intersection(historical_areas)
        if overlap:
            candidate["score"] += len(overlap) * 5
            candidate["areas"].update(overlap)

        if historical_pr.risk_level == "high":
            candidate["score"] += 1

    recommendations = []
    for name, data in candidates.items():
        reasons = []
        if data["areas"]:
            reasons.append(f"Previously shipped changes in {', '.join(sorted(data['areas'])[:2])}.")
        if data["recent_prs"]:
            reasons.append(f"Has {data['recent_prs']} recent PRs in this repository.")
        reasons.append(f"Has {data['pr_count']} historical PRs in this repository.")
        recommendations.append(
            {
                "reviewer": name,
                "score": data["score"],
                "reasons": reasons,
            }
        )

    recommendations.sort(key=lambda item: (-item["score"], item["reviewer"]))
    if recommendations:
        return recommendations[:limit]

    return [
        {
            "reviewer": "team-maintainer",
            "score": 1,
            "reasons": ["No recent file ownership history is available. Ask a repository maintainer to review."],
        }
    ]
