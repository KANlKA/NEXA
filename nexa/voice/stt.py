"""
stt.py

Speech-to-text using faster-whisper (a fast, local implementation of
OpenAI's open-source Whisper model). Fully offline after the model
downloads once — no API calls, no per-request cost.

Model sizes (speed vs accuracy tradeoff), roughly:
  tiny   - fastest, least accurate
  base   - good default, what we start with
  small  - noticeably more accurate, still fast on Apple Silicon
  medium - best accuracy, slower

Swap MODEL_SIZE below if accuracy isn't good enough once you're testing
with real commands.
"""

import numpy as np
from faster_whisper import WhisperModel

MODEL_SIZE = "small"  # upgraded from "base" — noticeably more accurate, still fast on Apple Silicon

# Same singleton pattern as everywhere else — loading the model is slow,
# transcribing with an already-loaded model is fast.
_model_instance = None


def _get_model() -> WhisperModel:
    global _model_instance
    if _model_instance is None:
        # compute_type="int8" keeps it fast and light on CPU.
        _model_instance = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    return _model_instance


def _normalize(audio: np.ndarray) -> np.ndarray:
    """
    Boosts quiet audio up to a consistent peak volume before transcribing.
    Whisper is prone to hallucinating plausible-sounding but WRONG text when
    given quiet/low-energy audio — normalizing gives it a stronger signal
    to work with, regardless of how close you were to the mic.
    """
    peak = np.abs(audio).max()
    if peak < 1e-4:  # essentially silent, nothing to normalize
        return audio
    target_peak = 0.9
    return audio * (target_peak / peak)


def transcribe(audio: np.ndarray) -> str:
    """
    audio: 1D float32 numpy array at 16kHz (same format our recording
           and speaker verification already use).
    Returns the transcribed text as a plain string.
    """
    audio = _normalize(audio)
    model = _get_model()
    segments, _info = model.transcribe(audio, language="en")
    # Whisper returns text in chunks ("segments") — join them into one string.
    text = " ".join(segment.text.strip() for segment in segments)
    return text.strip()
