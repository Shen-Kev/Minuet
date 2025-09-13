import tempfile
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

# ----- Model config -----
# Good starter model; add ".en" for English-only or try "small", "medium", "large-v3" for accuracy
MODEL_NAME = "base.en"
# CPU works; if you have NVIDIA GPU+CUDA, switch device="cuda", compute_type="float16"
model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")

app = FastAPI(title="Speech-to-Text (Faster-Whisper)")

# Dev-friendly CORS; in prod, lock this down to your domain(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # e.g. ["http://localhost:5173", "http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "model": MODEL_NAME}

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    # Guardrails
    if audio.size and audio.size > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50MB).")
    suffix = Path(audio.filename or "").suffix.lower()
    allowed = {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".webm", ".flac"}
    if suffix and suffix not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {suffix}")

    # Save to temp file, transcribe, then clean up
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix or ".bin") as tmp:
        tmp.write(await audio.read())
        tmp_path = Path(tmp.name)

    try:
        # Faster-Whisper uses ffmpeg internally; pass the path
        segments, info = model.transcribe(
            str(tmp_path),
            vad_filter=True,      # trim long silences
            beam_size=5,
            language="en",        # set None to auto-detect language
            # word_timestamps=True # enable if you want word-level timings
        )
        text_parts = [seg.text.strip() for seg in segments]
        return JSONResponse({
            "engine": "faster-whisper",
            "model": MODEL_NAME,
            "duration": info.duration,
            "language": info.language,
            "text": " ".join(t for t in text_parts if t)
        })
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
