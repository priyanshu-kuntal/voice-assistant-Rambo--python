import json
import os
import re
import subprocess
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from pathlib import Path


CONFIG_DIR = Path(__file__).parent / "config"
TARGETS_PATH = CONFIG_DIR / "targets.json"


def load_targets() -> dict[str, str]:
    if not TARGETS_PATH.exists():
        return {}
    try:
        return json.loads(TARGETS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def start_target(target: str) -> bool:
    """
    Start an app, open a URL, or open a Windows protocol (e.g. ms-settings:).
    """
    target = target.strip()
    if not target:
        return False

    if re.match(r"^https?://", target, flags=re.I):
        webbrowser.open(target)
        return True

    # Windows protocol handlers like ms-settings:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:$", target):
        subprocess.Popen(["cmd", "/c", "start", "", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True

    try:
        os.startfile(target)  # type: ignore[attr-defined]
        return True
    except Exception:
        try:
            subprocess.Popen(["cmd", "/c", "start", "", target], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            return False


@dataclass
class CommandResult:
    spoken: str
    ok: bool = True


class RamboCore:
    """
    Pure command router. No hotkeys, no microphone, no TTS.
    Safe to reuse from a server or UI.
    """

    def __init__(self) -> None:
        self.targets = load_targets()
        self._psutil = None
        self._pyautogui = None

    def _lazy_import_psutil(self):
        if self._psutil is None:
            import psutil  # type: ignore

            self._psutil = psutil
        return self._psutil

    def _lazy_import_pyautogui(self):
        if self._pyautogui is None:
            import pyautogui  # type: ignore

            self._pyautogui = pyautogui
        return self._pyautogui

    def handle_command(self, raw: str) -> CommandResult:
        text = normalize(raw)
        if not text:
            return CommandResult("I didn't catch that.", ok=False)

        if text in {"help", "what can you do", "what can you do rambo"}:
            return CommandResult(
                "Try: open notepad, open youtube, search for cats, type hello, lock my pc, battery."
            )

        if "time" in text and ("what" in text or "tell" in text):
            now = time.strftime("%I:%M %p").lstrip("0")
            return CommandResult(f"It is {now}.")

        if text in {"battery", "battery status"}:
            psutil = self._lazy_import_psutil()
            b = psutil.sensors_battery()
            if not b:
                return CommandResult("I can't read the battery on this device.", ok=False)
            plugged = "plugged in" if b.power_plugged else "on battery"
            return CommandResult(f"Battery is {int(b.percent)} percent, {plugged}.")

        m = re.match(r"^(search for|search)\s+(.+)$", text)
        if m:
            q = m.group(2).strip()
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}")
            return CommandResult(f"Searching for {q}.")

        m = re.match(r"^(open|launch|start)\s+(.+)$", text)
        if m:
            name = m.group(2).strip()
            target = self.targets.get(name, "") or name
            if start_target(target):
                return CommandResult(f"Opening {name}.")
            return CommandResult(f"I couldn't open {name}.", ok=False)

        m = re.match(r"^(type|write)\s+(.+)$", text)
        if m:
            payload = m.group(2)
            pyautogui = self._lazy_import_pyautogui()
            pyautogui.write(payload, interval=0.01)
            return CommandResult("Done.")

        if text in {"lock my pc", "lock pc", "lock computer", "lock"}:
            subprocess.Popen(
                ["rundll32.exe", "user32.dll,LockWorkStation"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return CommandResult("Locking.")

        if text in {"shutdown", "shut down", "power off"}:
            subprocess.Popen(["shutdown", "/s", "/t", "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return CommandResult("Shutting down.")

        if text in {"restart", "reboot"}:
            subprocess.Popen(["shutdown", "/r", "/t", "0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return CommandResult("Restarting.")

        return CommandResult("Sorry, I don't know that command yet.", ok=False)

