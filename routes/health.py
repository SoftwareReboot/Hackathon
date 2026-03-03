from flask import Blueprint, request, jsonify
from prompts.interview import interview_system_prompt
from prompts.coding import coding_system_prompt
from services.lm_client import client, MODEL

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health", methods=["GET"])
def health():
    """Quick check that Flask + LM Studio are both reachable."""
    try:
        models = client.models.list()
        return jsonify({"status": "ok", "models": [m.id for m in models.data]})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503