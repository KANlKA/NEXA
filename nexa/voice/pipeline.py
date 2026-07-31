"""
pipeline.py

The full voice loop, wiring together everything built so far:

  1. Wake word listener runs continuously in the background
  2. On detection -> record a few seconds of audio (the command)
  3. Check the recording against your voiceprint (speaker_id.verify)
  4. If it's you -> transcribe with Whisper -> hand off the text
     If it's not you -> ignore, go back to listening

Step 4's "hand off the text" is currently just printing it. This is
exactly the seam where Phase 2 (the orchestrator) will plug in later —
instead of print(text), it'll become bus.publish("command_transcribed", text).
"""

import asyncio
import logging
from nexa.config import get_config
from nexa.voice.wake_word import WakeWordListener
from nexa.voice.audio_utils import record_seconds, rms_level, save_wav, play_beep
from nexa.voice.speaker_id import verify
from nexa.voice.stt import transcribe
from nexa.voice.tts import speak
from nexa.registry import SkillRegistry
from nexa.orchestrator import Orchestrator
from nexa.skills.ping import PingSkill
from nexa.skills.app_control import OpenAppSkill

log = logging.getLogger("nexa.voice.pipeline")

COMMAND_RECORD_SECONDS = 5
QUIET_THRESHOLD = 0.01  # below this RMS, audio is likely too quiet for reliable STT

# Build the registry once at import time — add new skills here as we build them.
_registry = SkillRegistry()
_registry.register(PingSkill())
_registry.register(OpenAppSkill())
_orchestrator = Orchestrator(_registry)


def _on_wake_detected():
    print("\n🎙  Heard the wake word — recording your command...")
    play_beep()

    audio = record_seconds(COMMAND_RECORD_SECONDS)

    # Diagnostics: save every command recording to disk so we can actually
    # listen back to what Nexa captured, and flag if it looks too quiet.
    debug_path = str(get_config().data_dir / "debug_last_command.wav")
    save_wav(audio, debug_path)
    volume = rms_level(audio)
    log.info(f"Recording volume (RMS): {volume:.4f} — saved to {debug_path}")
    if volume < QUIET_THRESHOLD:
        print(f"⚠️  Recording was very quiet (RMS {volume:.4f}) — move closer to the mic or speak up.")

    is_match, score = verify(audio)
    log.info(f"Speaker check: match={is_match} score={score:.3f}")

    if not is_match:
        print(f"Voice not recognized (score {score:.3f}) — ignoring.")
        # Deliberately silent here — Nexa shouldn't announce that it heard
        # an unrecognized voice, it should just ignore it.
        return

    print("Voice confirmed — transcribing...")
    text = transcribe(audio)
    print(f'>>> Command: "{text}"')

    # Route through the orchestrator instead of just echoing the transcript.
    # asyncio.run() is fine here since this whole pipeline is otherwise
    # synchronous — it just spins up a fresh event loop for this one call.
    result = asyncio.run(_orchestrator.handle(text))
    print(f"<<< Result: success={result.success} response=\"{result.spoken_response}\"")
    speak(result.spoken_response)


def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("Nexa voice pipeline running. Say the wake word, then speak your command.")
    print("(Press Ctrl+C to stop)\n")

    listener = WakeWordListener(on_detected=_on_wake_detected, wakeword_model=_pick_wake_model())
    try:
        listener.listen_forever()
    except KeyboardInterrupt:
        print("\nNexa stopped.")


def _pick_wake_model() -> str:
    """
    Uses your trained "Hey Nexa" model if you've set wake_word_model_path
    in config.yaml, otherwise falls back to the "Hey Jarvis" placeholder
    we've been testing with.
    """
    cfg = get_config()
    if cfg.wake_word_model_path:
        print(f"Using custom wake word model: {cfg.wake_word_model_path}")
        return cfg.wake_word_model_path
    print("No custom wake word model configured — using 'Hey Jarvis' placeholder.")
    return "hey_jarvis"


if __name__ == "__main__":
    run()