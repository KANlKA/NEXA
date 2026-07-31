"""
llm.py

Thin wrapper around Ollama's local HTTP API. This is the ONLY place in
Nexa that talks to the LLM — every other module just calls ask() or
ask_structured() without knowing/caring that it's Ollama underneath.
That matters later: if you ever swap models or add a cloud fallback
(Groq/OpenRouter), you only change this one file.

Ollama runs as a background service on your Mac after installation,
listening on localhost:11434 — this is just a normal HTTP POST to it.
"""

import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:7b"


def ask(prompt: str, system: str = "") -> str:
    """
    Simple text-in, text-out call to the local model.
    """
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "system": system,
            "stream": False,  # get the full response at once, not token-by-token
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def ask_structured(prompt: str, system: str) -> dict:
    """
    Asks the model to respond with ONLY valid JSON (no explanation text),
    and parses it. This is how we get structured {skill, params} output
    for routing commands, instead of free-form text we'd have to guess-parse.

    `system` should explicitly instruct the model to output JSON only —
    see orchestrator.py for the actual prompt we use.
    """
    raw = ask(prompt, system=system)

    # Models sometimes wrap JSON in markdown code fences despite instructions
    # not to — strip those defensively rather than fail on it.
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON. Raw output: {raw!r}") from e
