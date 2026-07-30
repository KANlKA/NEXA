
import time
import threading
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
                     IMPORTANT: this runs on the main thread, AFTER the mic stream
                     used for wake word detection has been closed — so it's safe
                     for on_detected to open its own mic recording (e.g. to capture
                     your command) without conflicting with this listener.
        wakeword_model: which pretrained model to load. Swap this string for
                         "hey_nexa" once we train a custom model.
        """
        self.on_detected = on_detected
        self.model = Model(wakeword_models=[wakeword_model])
        self._triggered_recently = False  # simple cooldown to avoid re-firing every chunk
        self._trigger_event = threading.Event()

    def _audio_callback(self, indata, frames, time_info, status):
        if status:
            log.warning(f"Audio stream status: {status}")

        audio_chunk = indata[:, 0].astype(np.int16)
        predictions = self.model.predict(audio_chunk)

        for keyword, score in predictions.items():
            if score > DETECTION_THRESHOLD and not self._triggered_recently:
                log.info(f"Wake word '{keyword}' detected (confidence: {score:.2f})")
                self._triggered_recently = True
                # NOTE: we do NOT call on_detected() here. This callback runs on
                # sounddevice's internal audio thread — doing slow work (like
                # recording more audio) here would block that thread and can
                # deadlock the stream. Instead we just signal the main thread.
                self._trigger_event.set()
            elif score < DETECTION_THRESHOLD * 0.5:
                # reset cooldown once confidence drops back down
                self._triggered_recently = False

    def listen_forever(self):
        """
        Runs forever, alternating between two states:
          - LISTENING: mic stream open, watching for the wake word
          - HANDLING:  mic stream closed, on_detected() has full control of the mic
        This avoids ever having two audio streams open at once.
        """
        log.info("Wake word listener starting — say 'Hey Jarvis' to test.")
        while True:
            self._trigger_event.clear()
            self._triggered_recently = False
            # Clear openWakeWord's internal audio buffer. Without this, leftover
            # buffered audio from before the pause (recording the command,
            # transcribing, etc.) can bleed into the next session and cause
            # a false trigger the instant listening resumes.
            self.model.reset()

            with sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=1,
                dtype="int16",
                blocksize=CHUNK_SAMPLES,
                callback=self._audio_callback,
            ):
                # Block here (on the main thread) until the callback signals a detection.
                self._trigger_event.wait()
            # `with` block has exited by this point, so the mic stream is fully
            # closed and the device is free for on_detected() to use.

            self.on_detected()
            log.info("Resuming wake word listening...")
            # Brief pause before reopening the stream — gives any trailing audio
            # (echoes, your last words fading out) time to settle instead of
            # immediately feeding into the freshly reset buffer.
            time.sleep(0.75)
