
import numpy as np
from resemblyzer import VoiceEncoder
from nexa.config import get_config

# Loading the model is somewhat slow (~1-2s) and should only happen ONCE,
# not on every verification call — same singleton pattern as config/event_bus.
_encoder_instance = None


def _get_encoder() -> VoiceEncoder:
    global _encoder_instance
    if _encoder_instance is None:
        _encoder_instance = VoiceEncoder()
    return _encoder_instance


def _voiceprint_path():
    return get_config().data_dir / "voiceprint.npy"


def enroll_from_samples(audio_samples: list[np.ndarray]) -> None:
    """
    Takes several audio clips (numpy arrays) of your voice, averages
    their embeddings into one voiceprint, and saves it to disk.
    Using multiple samples (not just one) makes the voiceprint more
    robust to variation in your tone/volume/pace.
    """
    encoder = _get_encoder()
    embeddings = [encoder.embed_utterance(sample) for sample in audio_samples]
    voiceprint = np.mean(embeddings, axis=0)

    path = _voiceprint_path()
    np.save(path, voiceprint)
    print(f"Voiceprint saved to {path}")


def is_enrolled() -> bool:
    return _voiceprint_path().exists()


def verify(audio_sample: np.ndarray) -> tuple[bool, float]:
    """
    Compares a new audio clip against your saved voiceprint.
    Returns (is_match, similarity_score).
    """
    if not is_enrolled():
        raise RuntimeError("No voiceprint found — run enroll_voice.py first.")

    voiceprint = np.load(_voiceprint_path())
    encoder = _get_encoder()
    new_embedding = encoder.embed_utterance(audio_sample)

    # Cosine similarity: dot product of two normalized vectors.
    similarity = np.dot(voiceprint, new_embedding) / (
        np.linalg.norm(voiceprint) * np.linalg.norm(new_embedding)
    )

    threshold = get_config().speaker_similarity_threshold
    return bool(similarity > threshold), float(similarity)
