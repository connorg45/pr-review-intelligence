from collections import Counter, defaultdict

from app.models import EventLog, PullRequest, Repository


def get_dashboard_summary() -> dict:
    pull_requests = PullRequest.query.order_by(PullRequest.updated_at.desc()).all()
    repositories = Repository.query.order_by(Repository.full_name.asc()).all()
    recent_events = EventLog.query.order_by(EventLog.created_at.desc()).limit(8).all()

    total_prs = len(pull_requests)
    open_prs = sum(1 for pr in pull_requests if pr.state == "open")
    high_risk_prs = [pr for pr in pull_requests if pr.risk_level == "high"]
    analyzed = [pr for pr in pull_requests if pr.risk_score is not None]
    avg_risk_score = round(sum(pr.risk_score for pr in analyzed) / len(analyzed), 1) if analyzed else 0

    review_deltas = []
    for pr in pull_requests:
        if pr.first_review_at and pr.created_at:
            review_deltas.append((pr.first_review_at - pr.created_at).total_seconds() / 3600)
    avg_time_to_first_review_hours = round(sum(review_deltas) / len(review_deltas), 1) if review_deltas else None

    risk_distribution_counter = Counter(pr.risk_level or "unknown" for pr in pull_requests)
    risk_distribution = [
        {"level": level, "count": risk_distribution_counter.get(level, 0)}
        for level in ["low", "medium", "high"]
    ]

    trend_map = defaultdict(list)
    for pr in analyzed:
        trend_map[pr.updated_at.date().isoformat()].append(pr.risk_score)
    trend = []
    for date in sorted(trend_map.keys())[-7:]:
        values = trend_map[date]
        trend.append({"date": date, "avg_risk_score": round(sum(values) / len(values), 1), "pr_count": len(values)})

    high_risk_items = [pr.to_list_dict() for pr in sorted(high_risk_prs, key=lambda pr: pr.risk_score or 0, reverse=True)[:6]]

    return {
        "summary": {
            "total_prs": total_prs,
            "open_prs": open_prs,
            "high_risk_prs": len(high_risk_prs),
            "avg_risk_score": avg_risk_score,
            "avg_time_to_first_review_hours": avg_time_to_first_review_hours,
        },
        "risk_distribution": risk_distribution,
        "trend": trend,
        "high_risk_prs": high_risk_items,
        "recent_events": [event.to_dict() for event in recent_events],
        "repositories": [repo.to_dict() for repo in repositories],
    }
