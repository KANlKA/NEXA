from nexa.voice.audio_utils import record_seconds
from nexa.voice.stt import transcribe
TEST_SECONDS = 5
def main():
    input("Press Enter, then say a full sentence...")
    audio = record_seconds(TEST_SECONDS)
    print("Transcribing (first run downloads the model, ~1 min)...")
    text = transcribe(audio)
    print(f"\nTranscript: \"{text}\"")
if __name__ == "__main__":
    main()