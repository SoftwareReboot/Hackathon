from services import llm_service, prompt_service


def handle_health():
    models = llm_service.list_models()
    return {"status": "ok", "models": models}


def handle_chat(data: dict) -> str:
    phase         = data.get("phase", "interview")
    name          = data.get("name", "Candidate")
    role          = data.get("role", "Developer")
    category      = data.get("category", "")
    questions     = data.get("questions", [])
    messages      = data.get("messages", [])
    custom_prompt = data.get("customPrompt")

    if custom_prompt:
        system = custom_prompt
    elif phase == "coding":
        system = prompt_service.coding_system_prompt(name, role)
    else:
        system = prompt_service.interview_system_prompt(name, role, category, questions)

    return llm_service.chat_completion(system, messages)