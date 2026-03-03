import json


def strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` fences that some models wrap responses in."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        end = -1 if lines[-1] == "```" else len(lines)
        text = "\n".join(lines[1:end])
    return text.strip()


def safe_parse_json(raw: str) -> dict:
    cleaned = strip_markdown_fences(raw)
    return json.loads(cleaned)