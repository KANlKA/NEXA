import numpy as np
import sounddevice as sd
from openwakeword.model import Model
import logging

log = logging.getLogger("nexa.voice.wake_word")

SAMPLE_RATE = 16000          # openWakeWord expects 16kHz audio
CHUNK_SAMPLES = 1280          # ~80ms per chunk, openWakeWord's expected frame size
DETECTION_THRESHOLD = 0.5     # confidence score (0-1) needed to count as "heard it"


class WakeWordListener:
    def __init__(self, on_detected, wakeword_model: str = "hey_jarvis"):
        """
        on_detected: a callback function (no args) called when the wake word fires.
        wakeword_model: which pretrained model to load. Swap this string for
                         "hey_nexa" once we train a custom model.
        """
        self.on_detected = on_detected
        self.model = Model(wakeword_models=[wakeword_model])
        self._triggered_recently = False  # simple cooldown to avoid re-firing every chunk

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            log.warning(f"Audio stream status: {status}")

        audio_chunk = indata[:, 0].astype(np.int16)
        predictions = self.model.predict(audio_chunk)

        for keyword, score in predictions.items():
            if score > DETECTION_THRESHOLD and not self._triggered_recently:
                log.info(f"Wake word '{keyword}' detected (confidence: {score:.2f})")
                self._triggered_recently = True
                self.on_detected()
            elif score < DETECTION_THRESHOLD * 0.5:
                # reset cooldown once confidence drops back down
                self._triggered_recently = False

    def listen_forever(self):
        """Blocks forever, streaming mic audio into the detector."""
        log.info("Wake word listener starting — say 'Hey Jarvis' to test.")
        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16",
            blocksize=CHUNK_SAMPLES,
            callback=self._audio_callback,
        ):
            while True:
                sd.sleep(100)
