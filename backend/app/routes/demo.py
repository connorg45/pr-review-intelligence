from flask import Blueprint, jsonify

from app.services.demo_seed import seed_demo_data


demo_bp = Blueprint("demo", __name__)


@demo_bp.post("/demo/reset")
def reset_demo():
    result = seed_demo_data(reset=True)
    return jsonify({"message": "Demo data reset successfully.", **result})
