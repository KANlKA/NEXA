"""
Confirms Python can talk to your local Ollama server before we build
the orchestrator on top of it.
"""

from nexa.llm import ask, ask_structured

if __name__ == "__main__":
    print("Testing plain text response...")
    reply = ask("Say hello in exactly five words.")
    print(f"Model said: {reply}\n")

    print("Testing structured JSON response...")
    result = ask_structured(
        prompt="The user said: open Chrome",
        system=(
            "You are an intent parser. Respond with ONLY a JSON object, "
            'no other text, in this exact shape: {"skill": "<name>", "params": {}}'
        ),
    )
    print(f"Parsed dict: {result}")
