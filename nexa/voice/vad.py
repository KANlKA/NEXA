#uses silero vad, a model that tells how likely this is speech vs silence. We use it to record until the user stops talking, so we can then trans
import numpy as np
import sounddevice as sd
import torch

SAMPLE_RATE = 16000
CHUNK_SAMPLES = 512          # Silero VAD expects small chunks like this at 16kHz
SPEECH_PROB_THRESHOLD = 0.5

# Loaded once, reused — same singleton pattern as everywhere else in the project.
_vad_model = None


def _get_vad_model():
    global _vad_model
    if _vad_model is None:
        # torch.hub downloads this once and caches it locally (~2MB, tiny model)
        _vad_model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-vad", model="silero_vad", trust_repo=True
        )
    return _vad_model


def record_until_silence(max_seconds: float = 10.0, silence_duration: float = 1.0) -> np.ndarray:
    """
    Records from the mic, chunk by chunk, until `silence_duration` seconds
    of non-speech is detected, or `max_seconds` total is reached (safety cap).
    Returns the recorded audio as a 1D float32 numpy array.
    """
    model = _get_vad_model()
    chunks: list[np.ndarray] = []
    silent_chunks_needed = int(silence_duration * SAMPLE_RATE / CHUNK_SAMPLES)
    silent_streak = 0
    heard_speech_yet = False

    print("Listening for your command...")

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="float32") as stream:
        total_chunks = int(max_seconds * SAMPLE_RATE / CHUNK_SAMPLES)
        for _ in range(total_chunks):
            audio_chunk, _ = stream.read(CHUNK_SAMPLES)
            chunk = audio_chunk[:, 0]
            chunks.append(chunk)

            speech_prob = model(torch.from_numpy(chunk), SAMPLE_RATE).item()

            if speech_prob > SPEECH_PROB_THRESHOLD:
                heard_speech_yet = True
                silent_streak = 0
            elif heard_speech_yet:
                # Only start counting silence AFTER we've heard some speech —
                # otherwise it'd stop immediately, before you've said anything.
                silent_streak += 1
                if silent_streak >= silent_chunks_needed:
                    break

    print("Done listening.")
    return np.concatenate(chunks)
