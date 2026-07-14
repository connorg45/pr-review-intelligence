from flask import Blueprint, jsonify, request

from app.models import EventLog


events_bp = Blueprint("events", __name__)


@events_bp.get("/events")
def list_events():
    try:
        limit = int(request.args.get("limit", 50))
    except (TypeError, ValueError):
        return jsonify({"message": "Event limit must be a whole number between 1 and 200."}), 400
    if limit < 1 or limit > 200:
        return jsonify({"message": "Event limit must be between 1 and 200."}), 400
    events = EventLog.query.order_by(EventLog.created_at.desc()).limit(limit).all()
    return jsonify({"items": [event.to_dict() for event in events]})
