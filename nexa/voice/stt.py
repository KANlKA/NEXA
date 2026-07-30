import numpy as np
from faster_whisper import WhisperModel

MODEL_SIZE = "base"

# Same singleton pattern as everywhere else — loading the model is slow,
# transcribing with an already-loaded model is fast.
_model_instance = None


def _get_model() -> WhisperModel:
    global _model_instance
    if _model_instance is None:
        # compute_type="int8" keeps it fast and light on CPU.
        _model_instance = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model_instance


def transcribe(audio: np.ndarray) -> str:
    """
    audio: 1D float32 numpy array at 16kHz (same format our recording
           and speaker verification already use).
    Returns the transcribed text as a plain string.
    """
    model = _get_model()
    segments, _info = model.transcribe(audio, language="en")
    # Whisper returns text in chunks ("segments") — join them into one string.
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()
