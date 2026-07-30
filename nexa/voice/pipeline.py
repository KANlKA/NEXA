"""  
  1. Wake word listener runs continuously in the background
  2. On detection -> record a few seconds of audio (the command)
  3. Check the recording against your voiceprint (speaker_id.verify)
  4. If it's you -> transcribe with Whisper -> hand off the text
     If it's not you -> ignore, go back to listening
"""

import logging
from nexa.voice.wake_word import WakeWordListener
from nexa.voice.audio_utils import record_seconds
from nexa.voice.speaker_id import verify
from nexa.voice.stt import transcribe
 
log = logging.getLogger("nexa.voice.pipeline")
 
COMMAND_RECORD_SECONDS = 5
 
 
def _on_wake_detected():
    print("\n🎙  Heard the wake word — recording your command...")
 
    audio = record_seconds(COMMAND_RECORD_SECONDS)
 
    is_match, score = verify(audio)
    log.info(f"Speaker check: match={is_match} score={score:.3f}")
 
    if not is_match:
        print(f"Voice not recognized (score {score:.3f}) — ignoring.")
        return
 
    print("Voice confirmed — transcribing...")
    text = transcribe(audio)
    print(f'>>> Command: "{text}"')
 
    # --- Phase 2 will replace this print with a real orchestrator call ---
 
 
def run():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    print("Nexa voice pipeline running. Say the wake word, then speak your command.")
    print("(Press Ctrl+C to stop)\n")
 
    listener = WakeWordListener(on_detected=_on_wake_detected)
    try:
        listener.listen_forever()
    except KeyboardInterrupt:
        print("\nNexa stopped.")
 
 
if __name__ == "__main__":
    run()