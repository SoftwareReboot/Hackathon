from flask import Blueprint, request, jsonify
from controllers import report_controller

report_bp = Blueprint("report", __name__)


@report_bp.post("/report")
def report():
    try:
        data        = request.get_json(force=True)
        report_data = report_controller.handle_report(data)
        return jsonify(report_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500