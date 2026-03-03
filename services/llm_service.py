from services import llm_service, prompt_service
from utils.json_utils import safe_parse_json


def handle_report(data: dict) -> dict:
    name    = data.get("name", "Candidate")
    role    = data.get("role", "Developer")
    history = data.get("history", [])

    transcript = prompt_service.build_transcript(history)
    prompt     = prompt_service.report_prompt(name, role, transcript)
    raw        = llm_service.single_completion(prompt)

    return safe_parse_json(raw)