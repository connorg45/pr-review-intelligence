from flask import Blueprint, jsonify

from app.services.dashboard_service import get_dashboard_summary


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/dashboard/summary")
def dashboard_summary():
    return jsonify(get_dashboard_summary())
