
import subprocess
import tempfile
from pathlib import Path

# Where we'll keep the downloaded voice model. One-time download, see README.
PIPER_MODEL_PATH = Path.home() / ".nexa" / "piper_voice" / "en_US-lessac-medium.onnx"


def speak(text: str) -> None:
    """
    Synthesizes `text` to speech and plays it immediately.
    Uses a temp wav file as the handoff between Piper (synthesis)
    and afplay (macOS's built-in audio player) — simple and reliable.
    """
    if not text.strip():
        return

    if not PIPER_MODEL_PATH.exists():
        raise RuntimeError(
            f"Piper voice model not found at {PIPER_MODEL_PATH}. "
            "See README.md for the one-time download step."
        )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    # Piper reads text from stdin, writes synthesized audio to --output_file
    subprocess.run(
        ["piper", "--model", str(PIPER_MODEL_PATH), "--output_file", wav_path],
        input=text.encode("utf-8"),
        check=True,
        capture_output=True,
    )

    # afplay ships with macOS — no extra dependency needed to play it back
    subprocess.run(["afplay", wav_path], check=True)
