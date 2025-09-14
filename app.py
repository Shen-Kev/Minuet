# app.py
# A minimal, robust FastAPI backend for browser-recorded audio -> text
# Uses open-source Faster-Whisper. CPU-friendly by default.

import os
import tempfile
import logging
import traceback
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
import anthropic

anthropic_client = anthropic.Anthropic(api_key="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")




from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel


# --------------------------
# Config (override via env):
# --------------------------
MODEL_NAME   = os.getenv("STT_MODEL", "base.en")     # tiny/base/small/medium/large-v3 (add .en for english-only)
DEVICE       = os.getenv("STT_DEVICE", "cpu")        # "cpu" or "cuda"
COMPUTE_TYPE = os.getenv("STT_COMPUTE", "int8")      # good on CPU. GPU: "float16"
LANGUAGE     = os.getenv("STT_LANGUAGE", "")         # "" => auto-detect; e.g., "en", "es", etc.
VAD_FILTER   = os.getenv("STT_VAD", "1") == "1"      # Voice activity detection

# Allow localhost dev & file:// pages (origin "null")
ALLOW_ORIGIN_REGEX = os.getenv("STT_ALLOW_ORIGIN_REGEX", ".*")

# --------------------------
# Logging
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("stt")

# --------------------------
# App & CORS
# --------------------------
app = FastAPI(title="Speech-to-Text Backend (Faster-Whisper)")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,   # works for http://localhost:* and file:// (origin "null")
    allow_credentials=False,                 # keep False so "*" can be used safely if you change to allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------
# Utilities
# --------------------------
def ffmpeg_ok() -> bool:
    try:
        out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return out.returncode == 0
    except Exception:
        return False

_MODEL: Optional[WhisperModel] = None

def get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        log.info(f"Loading Faster-Whisper model '{MODEL_NAME}' on {DEVICE} ({COMPUTE_TYPE})...")
        _MODEL = WhisperModel(MODEL_NAME, device=DEVICE, compute_type=COMPUTE_TYPE)
        log.info("Model loaded.")
    return _MODEL

def friendly_error(detail: str, status: int = 400) -> HTTPException:
    return HTTPException(status_code=status, detail=detail)

# --------------------------
# Routes
# --------------------------
@app.get("/health")
def health():
    return {
        "ok": True,
        "ffmpeg": ffmpeg_ok(),
        "model": MODEL_NAME,
        "device": DEVICE,
        "compute_type": COMPUTE_TYPE,
        "language": LANGUAGE or None,
        "vad_filter": VAD_FILTER,
    }


#def ask_claude(prompt: str) -> str:
#    msg = anthropic_client.messages.create(
#        model="claude-opus-4-1-20250805",
#        max_tokens=100,
#        temperature=0.2,
#        messages=[{"role": "user", "content": prompt}],
#    )
#    return "".join(part["text"] for part in msg.content if part["type"] == "text")

    



@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Accepts multipart/form-data with field name 'audio'.
    The file can be .wav/.webm/.ogg/.m4a/.mp3 etc. Faster-Whisper will decode via ffmpeg.
    Returns { text, words, segments, ... }.
    """
    # Basic introspection (helps when debugging from your browser console)
    log.info(f"Incoming file: name='{audio.filename}' type='{audio.content_type}'")

    # Save to a temporary file on disk so ffmpeg can read it
    suffix = Path(audio.filename or "").suffix
    if len(suffix) == 0:
        # default to .wav if no extension
        suffix = ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        file_bytes = await audio.read()
        if not file_bytes:
            raise friendly_error("Uploaded file is empty.", 400)
        tmp.write(file_bytes)

    try:
        # Ensure ffmpeg is available for decoding
        if not ffmpeg_ok():
            raise friendly_error(
                "ffmpeg is not installed or not on PATH. Install ffmpeg and try again.",
                500,
            )

        # Load (or reuse) model
        model = get_model()

        # Prepare options
        lang = LANGUAGE if LANGUAGE.strip() else None
        log.info(f"Transcribing '{tmp_path.name}' (lang={lang or 'auto'}, vad={VAD_FILTER})")

        # Do the transcription
        segments, info = model.transcribe(
            str(tmp_path),
            vad_filter=VAD_FILTER,
            word_timestamps=True,
            language=lang,          # None = auto-detect
            beam_size=5,
        )

        # Aggregate
        text_parts: List[str] = []
        out_segments: List[Dict[str, Any]] = []
        out_words: List[Dict[str, Any]] = []

        for seg in segments:
            text_parts.append(seg.text or "")
            out_segments.append({
                "id": seg.id,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "avg_logprob": seg.avg_logprob,
                "no_speech_prob": getattr(seg, "no_speech_prob", None),
                "compression_ratio": getattr(seg, "compression_ratio", None),
            })
            if seg.words:
                for w in seg.words:
                    out_words.append({
                        "word": w.word,
                        "start": w.start,
                        "end": w.end,
                        "prob": w.probability,
                    })

        transcript = " ".join(t.strip() for t in text_parts).strip()
        prompt = "summarize this: " + transcript

       #  Send request to Claude
        message = anthropic_client.messages.create(
            model="claude-opus-4-1-20250805",  # You can also use haiku (cheaper) or opus (stronger)
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ]

        )
        # Print Claude’s reply as minuet
        llm_reply = message.content[0].text


        return JSONResponse({
            "engine": "faster-whisper",
            "model": MODEL_NAME,
            "device": DEVICE,
            "compute_type": COMPUTE_TYPE,
            "duration": getattr(info, "duration", None),
            "language": getattr(info, "language", None),
            "text": llm_reply,
            "segments": out_segments,
            "words": out_words,
        })

    except HTTPException:
        raise
    except Exception as e:
        log.error("Transcription failed:\n" + traceback.format_exc())
        # Surface a helpful error to the browser
        raise friendly_error(f"Transcription failed: {e}", 500)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
