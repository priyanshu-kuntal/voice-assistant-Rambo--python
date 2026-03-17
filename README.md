# RAMBO Voice Assistant (Windows)

RAMBO runs in the background and starts listening **only when you press a hotkey**. It then performs the action you say (open apps/sites, search the web, type text, basic system commands).

It also includes:

- a **Web Control Panel** (`web/index.html`)
- an **Android remote app (APK)** in `mobile/` (Flutter)
- a **local RAMBO Server** (`rambo_server.py`) that both the web UI and Android app call

## What it can do (examples)

- **Open apps / targets**
  - "open notepad"
  - "open chrome"
  - "open settings"
- **Open websites**
  - "open youtube"
  - "open github"
- **Search**
  - "search for python speech recognition"
- **Type into current app**
  - "type hello from rambo"
- **System**
  - "lock my pc"
  - "shutdown" / "restart"
- **Info**
  - "what time is it"
  - "battery"

## Hotkey

- Default: **Ctrl + Alt + R**
- Press it once: RAMBO listens for a short phrase and executes it.
- Press it twice quickly: RAMBO stops talking (panic stop).

## Setup (Windows 10/11)

### 1) Install Python

Install Python 3.10+ and **check “Add Python to PATH”** during install.

After installing, open PowerShell and confirm:

```powershell
python --version
pip --version
```

### 2) Install dependencies

In this folder:

```powershell
cd e:\priyanshu
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Microphone dependency note (PyAudio)

`SpeechRecognition` usually uses **PyAudio** for microphone input. If `pip install pyaudio` fails, try:

```powershell
pip install pipwin
pipwin install pyaudio
```

If you still can’t get PyAudio working, you can still use RAMBO’s **typed fallback**: press the hotkey and type the command into the console when prompted.

### 3) Run RAMBO

```powershell
python rambo.py
```

## Run RAMBO Server (for Web + Android)

Start the server (it prints a **Token** you must paste into the frontend/app):

```powershell
cd e:\priyanshu
.\.venv\Scripts\Activate.ps1
python -m uvicorn rambo_server:app --host 0.0.0.0 --port 8787
```

- Web UI on same laptop uses: `http://127.0.0.1:8787`
- Phone on same Wi‑Fi uses: `http://<your-laptop-ip>:8787`

Optional: set a fixed token (instead of a random token each run):

```powershell
$env:RAMBO_TOKEN = "my-secret-token"
python -m uvicorn rambo_server:app --host 0.0.0.0 --port 8787
```

## Web frontend (Control Panel)

Open `web\index.html` in your browser (double-click it).

Fill:

- **Server URL**: `http://127.0.0.1:8787` (or your laptop IP)
- **Token**: printed by the server

Then send commands like: `open notepad`, `search for cats`, `lock my pc`.

## Android APK (RAMBO Remote)

The Flutter app source is in `mobile/`.

See `mobile\README.md` for:

- `flutter pub get`
- `flutter run`
- `flutter build apk --release`

## Customize "open ..." targets

Edit `config\targets.json` to add your own apps/sites.

## Safety

Commands like shutdown/restart are enabled. If you want to disable them, remove them from `rambo.py` in `handle_command()`.

