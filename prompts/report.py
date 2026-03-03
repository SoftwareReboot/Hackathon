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