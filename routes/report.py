from flask import Blueprint, request, jsonify
from prompts.interview import interview_system_prompt
from prompts.coding import coding_system_prompt
from services.lm_client import client, MODEL

report_bp = Blueprint("report", __name__)

@report_bp.route("/api/report", methods=["POST"])
def report():
    """
    End-of-session evaluation endpoint.

    Expected body:
    {
        "name":     "Juan",
        "role":     "Full Stack Developer",
        "history":  [
            { "role": "user", "content": "...", "phase": "interview", "cat": "Behavioral" },
            { "role": "assistant", "content": "...", "phase": "interview", "cat": "Behavioral" },
            ...
        ]
    }
    """
    data    = request.get_json(force=True)
    name    = data.get("name", "Candidate")
    role    = data.get("role", "Developer")
    history = data.get("history", [])

    # Build plain transcript
    transcript = "\n\n".join(
        f"[{h.get('phase','').upper()} · {h.get('cat','')}] {h['role'].upper()}: {h['content']}"
        for h in history
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=900,
            temperature=0.3,
            messages=[
                {"role": "user", "content": report_prompt(name, role, transcript)}
            ]
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model wraps in ```json
        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

        import json
        report_data = json.loads(raw)
        return jsonify(report_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500