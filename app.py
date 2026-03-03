# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)  # allows React (localhost:3000) to call Flask (localhost:5000)

# ── LM Studio client ──────────────────────────────────────────────────────────
# LM Studio exposes an OpenAI-compatible API — no API key needed locally
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # any string works
)

MODEL = os.getenv("LM_MODEL", "qwen2.5-14b-instruct")


# ── Prompt builders ───────────────────────────────────────────────────────────

def interview_system_prompt(name, role, category, questions):
    q_list = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
    return f"""You are ALEX, a brutally direct senior technical interviewer at a top tech company hiring for a {role} position.
Candidate name: {name}
Current section: {category}

Your question list for this section (ask them in order, one per exchange):
{q_list}

BEHAVIOR RULES:
- Direct, impatient, challenging. Never accept vague or generic answers.
- Challenge weak answers: "That's too vague, give me a real example.", "What exactly did YOU do?", "What was the actual outcome?"
- After a strong answer: briefly acknowledge then immediately ask the next question.
- After a weak answer: push back ONCE, then move on.
- Keep ALL responses to 2-4 sentences max. One question per turn only.
- After the candidate answers 5 questions in this section, add [NEXT_SECTION] at the very end.

Always end with this JSON on its own line (never skip):
{{"conf":<0-100>,"clarity":<0-100>,"depth":<0-100>,"rel":<0-100>,"note":"<10 words max>"}}"""


def coding_system_prompt(name, role):
    return f"""You are ALEX, a ruthless senior engineer running a live coding interview for a {role} candidate named {name}.

BEHAVIOR RULES:
- Give ONE focused coding problem for {role}. State it clearly in 2-3 sentences, then wait.
- Aggressively challenge every response: "What is the time complexity?", "Why not use X?", "What if input is null?", "That breaks on edge case Y.", "Explain that line."
- Demand the candidate think out loud at every step.
- If they give a short or vague answer: "Keep talking. Walk me through it step by step."
- Never give hints. Be relentless. 2-3 sentences max per response.

Always end with this JSON on its own line (never skip):
{{"conf":<0-100>,"clarity":<0-100>,"depth":<0-100>,"rel":<0-100>,"note":"<10 words max>"}}"""


def report_prompt(name, role, transcript):
    return f"""You are a senior hiring panel lead. Evaluate this complete IT job interview.

Candidate: {name} | Target Role: {role}

FULL TRANSCRIPT:
{transcript}

Respond ONLY with this exact JSON (no markdown, no extra text):
{{
  "overall": <0-100>,
  "interview_score": <0-100>,
  "coding_score": <0-100>,
  "behavioral": <0-100>,
  "technical": <0-100>,
  "situational": <0-100>,
  "career": <0-100>,
  "hire": "<Strong Yes | Yes | Maybe | No | Strong No>",
  "verdict": "<3 honest sentences summarizing the candidate>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weaknesses": ["<weakness 1>", "<weakness 2>", "<weakness 3>"]
}}"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    """Quick check that Flask + LM Studio are both reachable."""
    try:
        models = client.models.list()
        return jsonify({"status": "ok", "models": [m.id for m in models.data]})
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503


@app.route("/api/chat", methods=["POST"])
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


@app.route("/api/report", methods=["POST"])
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


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000)