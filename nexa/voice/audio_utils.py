"""
audio_utils.py

Shared helper for recording a fixed-length clip from the mic.
Both voice enrollment and (later) command recording after the wake word
need this same "record N seconds, return it as a numpy array" behavior.
"""

import wave
import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # matches what both openWakeWord and Resemblyzer expect

def rms_level(audio: np.ndarray) -> float:
    """Return the root-mean-square loudness of an audio buffer."""
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio.astype(np.float32)))))

def record_seconds(duration: float) -> np.ndarray:
    """
    Records `duration` seconds of mono audio from the default mic.
    Returns a 1D float32 numpy array (values between -1 and 1),
    which is the format Resemblyzer expects.
    """
    print(f"Recording for {duration:.1f}s... speak now.")
    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )
    sd.wait()  # blocks until recording finishes
    print("Done recording.")
    return recording[:, 0]


def play_beep() -> None:
    """
    Plays a short, instant acknowledgment tone (~150ms) instead of a spoken
    "Yes?" — generating and playing a raw tone has near-zero latency, unlike
    TTS synthesis, which took long enough that the start of commands was
    getting cut off before recording even began.
    """
    duration = 0.15
    freq = 880  # a clean, noticeable "ding" pitch
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = (0.3 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    sd.play(tone, samplerate=SAMPLE_RATE)
    sd.wait()


def save_wav(audio: np.ndarray, path: str) -> None:
    """
    Saves a recorded clip to a real .wav file you can open and listen to.
    Used as a debugging tool — if Nexa mishears you, playing back exactly
    what it recorded tells you whether the problem is the recording itself
    (mic/volume/timing) or the transcription model.
    """
    audio_int16 = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)  # 16-bit
        f.setframerate(SAMPLE_RATE)
        f.writeframes(audio_int16.tobytes())
