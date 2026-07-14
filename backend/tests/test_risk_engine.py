from datetime import datetime, timedelta, timezone

from app.services.risk_engine import analyze_pull_request


def test_risk_engine_flags_large_sensitive_change_without_tests():
    result = analyze_pull_request(
        {
            "additions": 680,
            "deletions": 260,
            "changed_files_count": 12,
            "state": "open",
            "created_at": datetime.now(timezone.utc) - timedelta(days=14),
            "files": [
                {"path": "backend/app/services/auth.py", "is_sensitive": True, "is_test_file": False},
                {"path": "backend/migrations/versions/005_roles.py", "is_sensitive": True, "is_test_file": False},
                {"path": ".github/workflows/ci.yml", "is_sensitive": True, "is_test_file": False},
            ],
        }
    )

    assert result["risk_level"] == "high"
    assert result["risk_score"] >= 65
    assert any("sensitive" in reason.lower() for reason in result["reasons"])


def test_risk_engine_returns_low_risk_for_small_tested_change():
    result = analyze_pull_request(
        {
            "additions": 28,
            "deletions": 10,
            "changed_files_count": 2,
            "state": "closed",
            "created_at": datetime(2026, 3, 10, tzinfo=timezone.utc),
            "files": [
                {"path": "frontend/src/components/button.tsx", "is_sensitive": False, "is_test_file": False},
                {"path": "frontend/src/components/button.test.tsx", "is_sensitive": False, "is_test_file": True},
            ],
        }
    )

    assert result["risk_level"] == "low"
    assert result["risk_score"] < 35
    assert result["reasons"]
