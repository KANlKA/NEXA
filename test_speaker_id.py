from nexa.voice.audio_utils import record_seconds
from nexa.voice.speaker_id import verify, is_enrolled

TEST_SECONDS = 4
def main():
    if not is_enrolled():
        print("No voiceprint found yet — run enroll_voice.py first.")
        return
    input("Press Enter, then speak for a few seconds...")
    audio = record_seconds(TEST_SECONDS)

    is_match, score = verify(audio)
    print(f"\nSimilarity score: {score:.3f}")
    if is_match:
        print("MATCH — Nexa would respond to this voice.")
    else:
        print("NO MATCH — Nexa would ignore this voice.")


if __name__ == "__main__":
    main()
