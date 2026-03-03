from flask import Blueprint, request, jsonify
from prompts.interview import interview_system_prompt
from prompts.coding import coding_system_prompt
from services.lm_client import client, MODEL

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    """
    Main interview chat endpoint.

    Expected body:
    {
        "phase":     "interview" | "coding",
        "name":      "Juan",
        "role":      "Full Stack Developer",
        "category":  "Behavioral",           # only for interview phase
        "questions": ["q1", "q2", ...],      # only for interview phase (5 picked)
        "messages":  [                       # full conversation history
            { "role": "user",      "content": "..." },
            { "role": "assistant", "content": "..." },
            ...
        ]
    }
    """
    data = request.get_json(force=True)

    phase        = data.get("phase", "interview")
    name         = data.get("name", "Candidate")
    role         = data.get("role", "Developer")
    category     = data.get("category", "")
    questions    = data.get("questions", [])
    messages     = data.get("messages", [])
    custom_prompt = data.get("customPrompt", None)

    # Use customPrompt from frontend if provided, otherwise build server-side
    if custom_prompt:
        system = custom_prompt
    elif phase == "coding":
        system = coding_system_prompt(name, role)
    else:
        system = interview_system_prompt(name, role, category, questions)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=400,
            temperature=0.85,
            messages=[
                {"role": "system", "content": system},
                *messages
            ]
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500