import numpy as np
import sounddevice as sd

SAMPLE_RATE = 16000  # matches what both openWakeWord and Resemblyzer expect


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