from datetime import datetime, timezone

from app.utils.file_flags import classify_area, is_sensitive_path, is_test_file
from app.utils.time import as_utc


ENGINE_VERSION = "v1.0"


def analyze_pull_request(snapshot: dict) -> dict:
    additions = snapshot.get("additions", 0) or 0
    deletions = snapshot.get("deletions", 0) or 0
    changed_files_count = snapshot.get("changed_files_count", 0) or 0
    files = snapshot.get("files", [])
    state = snapshot.get("state", "open")
    created_at = snapshot.get("created_at")
    total_lines = additions + deletions
    distinct_areas = {classify_area(file.get("path", "")) for file in files if file.get("path")}

    score = 0
    reasons: list[str] = []

    if total_lines >= 900:
        score += 30
        reasons.append(f"Large change set with {total_lines} total lines modified.")
    elif total_lines >= 450:
        score += 20
        reasons.append(f"Substantial change set with {total_lines} total lines modified.")
    elif total_lines >= 200:
        score += 10
        reasons.append(f"Touches {total_lines} total lines, which raises review complexity.")

    if changed_files_count >= 20:
        score += 22
        reasons.append(f"Touches {changed_files_count} files, increasing cross-file review risk.")
    elif changed_files_count >= 10:
        score += 12
        reasons.append(f"Touches {changed_files_count} files across multiple areas.")

    if len(distinct_areas) >= 4:
        score += 8
        reasons.append(f"Spans {len(distinct_areas)} code areas, which broadens the review surface.")

    sensitive_files = [file for file in files if file.get("is_sensitive") or is_sensitive_path(file.get("path", ""))]
    if sensitive_files:
        score += min(24, 8 + len(sensitive_files) * 4)
        paths = ", ".join(file["path"] for file in sensitive_files[:3])
        reasons.append(f"Touches {len(sensitive_files)} sensitive paths, including {paths}.")

    migration_files = [file for file in files if "migration" in file.get("path", "").lower()]
    if migration_files:
        score += 14
        reasons.append("Database migration files were changed.")

    workflow_files = [file for file in files if ".github/workflows/" in file.get("path", "").lower()]
    if workflow_files:
        score += 10
        reasons.append("CI or workflow configuration changed.")

    backend_or_core = [
        file
        for file in files
        if any(token in classify_area(file.get("path", "")) for token in {"backend", "app", "src/api", "src/core"})
    ]
    test_files = [file for file in files if file.get("is_test_file") or is_test_file(file.get("path", ""))]
    if backend_or_core and not test_files:
        score += 14
        reasons.append("Backend or core logic changed without any accompanying test file updates.")

    if state == "open" and created_at:
        age_days = (datetime.now(timezone.utc) - as_utc(created_at)).days
        if age_days >= 21:
            score += 10
            reasons.append(f"PR has been open for {age_days} days, increasing merge and context risk.")
        elif age_days >= 10:
            score += 5
            reasons.append(f"PR has been open for {age_days} days and may be going stale.")

    if additions >= 500 and deletions >= 200:
        score += 8
        reasons.append("Large simultaneous additions and deletions suggest a substantial refactor.")

    score = min(score, 100)

    if score >= 65:
        level = "high"
    elif score >= 35:
        level = "medium"
    else:
        level = "low"

    if not reasons:
        reasons.append("Scoped change with limited churn and no major risk signals detected.")

    return {
        "engine_version": ENGINE_VERSION,
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons,
    }
