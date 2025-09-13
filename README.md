# Minuet
hackmit lmao

everyone type ur name in here and commit to see if it works
## kevin
## mingo
## Chloe
## Ellie





# Current functionality of just text to speech made by chatgpt

Speech-to-Text Demo (FastAPI + Frontend)

This project provides a simple end-to-end speech-to-text demo using:

Backend → FastAPI
 + Faster-Whisper
 (open-source Whisper inference)

Frontend → single HTML page with microphone recording, upload, and automatic transcription display

📦 Installation
1. Clone or copy project files

You should have at least:

app.py (backend)

requirements.txt

stt-frontend.html

2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

3. Install dependencies
pip install -r requirements.txt


⚠️ If you use zsh, remember to quote extras manually when needed:

pip install "uvicorn[standard]"

4. Install ffmpeg

Backend uses ffmpeg to decode audio.

macOS: brew install ffmpeg

Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y ffmpeg

Windows: winget install Gyan.FFmpeg

Verify:

ffmpeg -version

🚀 Running the Backend

Start FastAPI with Uvicorn:

uvicorn app:app --reload


Backend runs on http://127.0.0.1:8000
.

Health check: http://127.0.0.1:8000/health

API docs: http://127.0.0.1:8000/docs

🎤 Running the Frontend

Option 1: Open file directly
Double-click stt-frontend.html to open in your browser.
(some browsers block file:// CORS — if you see errors, use option 2)

Option 2: Serve locally

python -m http.server 5500


Then open http://127.0.0.1:5500/stt-frontend.html

🛠 Using the App

In the frontend, check Backend URL → should be http://localhost:8000/transcribe

Press Check Health → should return OK

Click Start Recording, speak, then Stop

Watch upload progress and transcript appear

Options:

Copy transcript to clipboard

Download full JSON (including word-level timestamps)

⚙️ Configuration

You can control backend behavior via environment variables:

# Default values shown
export STT_MODEL=base.en      # tiny/base/small/medium/large-v3
export STT_DEVICE=cpu         # or "cuda" for GPU
export STT_COMPUTE=int8       # good on CPU, use float16 on GPU
export STT_LANGUAGE=""        # "" = auto-detect, or force "en", "es", etc.
export STT_VAD=1              # 1=enable voice activity detection


Example (GPU + better model):

STT_MODEL=small.en STT_DEVICE=cuda STT_COMPUTE=float16 uvicorn app:app --reload

✅ Quick Test Without UI

Upload any audio file:

curl -F "audio=@example.wav" http://127.0.0.1:8000/transcribe

🧩 Troubleshooting

CORS error: serve HTML via http.server instead of file://

ffmpeg missing: check /health, install ffmpeg

No transcript: check backend logs, confirm audio is non-empty

Slow transcription: use smaller model (tiny.en or base.en)

🎯 Goals of this project

Free, open-source STT pipeline

Works entirely offline (no paid APIs)

Beginner-friendly: minimal setup, clear error messages

Extendable: add diarization, translation, or timestamps later