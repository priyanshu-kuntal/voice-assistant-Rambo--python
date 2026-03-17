import time
from typing import Optional

from rambo_core import RamboCore

HOTKEY = "ctrl+alt+r"
PANIC_STOP_WINDOW_S = 0.9


def _lazy_imports():
    """
    Keep imports lazy so the script can start even if some optional deps
    (like PyAudio) aren't installed yet.
    """
    import keyboard  # type: ignore
    import psutil  # type: ignore
    import pyautogui  # type: ignore
    import pyttsx3  # type: ignore
    import speech_recognition as sr  # type: ignore

    return keyboard, pyttsx3, sr


class Rambo:
    def __init__(self) -> None:
        self.core = RamboCore()
        self._engine = None
        self._last_hotkey_time = 0.0

        keyboard, pyttsx3, sr = _lazy_imports()
        self.keyboard = keyboard
        self.pyttsx3 = pyttsx3
        self.sr = sr

    def speak(self, text: str) -> None:
        if self._engine is None:
            self._engine = self.pyttsx3.init()
            self._engine.setProperty("rate", 185)
        self._engine.say(text)
        self._engine.runAndWait()

    def stop_speaking(self) -> None:
        if self._engine is not None:
            try:
                self._engine.stop()
            except Exception:
                pass

    def listen_once(self) -> Optional[str]:
        """
        Returns recognized text, or None if speech isn't available.
        """
        r = self.sr.Recognizer()

        try:
            with self.sr.Microphone() as source:
                r.adjust_for_ambient_noise(source, duration=0.4)
                audio = r.listen(source, timeout=4, phrase_time_limit=7)
        except Exception:
            return None

        try:
            # Online recognizer (fast/easy). Change to other engines if desired.
            return r.recognize_google(audio)
        except Exception:
            return ""

    def get_typed_fallback(self) -> str:
        try:
            return input("RAMBO (typed fallback). Enter command: ").strip()
        except EOFError:
            return ""

    def on_hotkey(self) -> None:
        now = time.time()
        if now - self._last_hotkey_time <= PANIC_STOP_WINDOW_S:
            self.stop_speaking()
            return
        self._last_hotkey_time = now

        self.speak("Listening.")
        heard = self.listen_once()
        if heard is None:
            cmd = self.get_typed_fallback()
        else:
            cmd = heard

        if cmd.strip().lower() in {"exit", "quit", "stop rambo"}:
            raise SystemExit(0)

        res = self.core.handle_command(cmd)
        self.speak(res.spoken)

    def run(self) -> None:
        print(f"RAMBO is running. Hotkey: {HOTKEY}")
        print("Say 'help' after pressing the hotkey for examples.")
        self.keyboard.add_hotkey(HOTKEY, self.on_hotkey, suppress=False, trigger_on_release=True)
        self.keyboard.wait()


def main() -> None:
    try:
        Rambo().run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

