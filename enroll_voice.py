from nexa.voice.audio_utils import record_seconds
from nexa.voice.speaker_id import enroll_from_samples

NUM_SAMPLES = 4
SECONDS_PER_SAMPLE = 4

PROMPTS = [
    "Say something like: Hey Nexa, what's the weather today.",
    "Now try: Open Chrome and play my playlist.",
    "Now: Nexa, remind me about my meeting tomorrow.",
    "Last one, talk normally for a few seconds about anything.",
]


def main():
    print("=== Nexa voice enrollment ===")
    print(f"We'll record {NUM_SAMPLES} short samples of your voice.\n")

    samples = []
    for i, prompt in enumerate(PROMPTS[:NUM_SAMPLES], start=1):
        input(f"\nSample {i}/{NUM_SAMPLES} — {prompt}\nPress Enter when ready...")
        audio = record_seconds(SECONDS_PER_SAMPLE)
        samples.append(audio)

    print("\nProcessing samples and saving voiceprint...")
    enroll_from_samples(samples)
    print("\nEnrollment complete. Run test_speaker_id.py to verify it recognizes you.")


if __name__ == "__main__":
    main()
