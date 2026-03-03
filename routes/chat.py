from flask import Blueprint, request, jsonify
from controller import chat_controller

chat_bp = Blueprint("chat", __name__)


@chat_bp.get("/health")
def health():
    try:
        result = chat_controller.handle_health()
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503


@chat_bp.post("/chat")
def chat():
    try:
        data  = request.get_json(force=True)
        reply = chat_controller.handle_chat(data)
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"error": str(e)}), 500