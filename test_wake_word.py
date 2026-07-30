import logging
from nexa.voice.wake_word import WakeWordListener

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def on_wake():
    print(">>> WAKE WORD DETECTED — this is where Nexa would start listening for your command")


if __name__ == "__main__":
    listener = WakeWordListener(on_detected=on_wake)
    listener.listen_forever()