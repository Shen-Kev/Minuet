# app.py
# A minimal, robust FastAPI backend for browser-recorded audio -> text
# Uses open-source Faster-Whisper. CPU-friendly by default.
# Test comment for Ellie

# app.py
import os
import tempfile
import logging
import traceback
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import requests
import anthropic

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

# --------------------------
# Root route
# --------------------------
from fastapi.responses import RedirectResponse
from fastapi import FastAPI

app = FastAPI(title="Minuet STT Backend")

@app.get("/")
def root():
    # Option 1: Simple JSON confirmation
    return {"message": "Minuet backend is running!"}

    # Option 2: Redirect to FastAPI docs automatically
    # return RedirectResponse(url="/docs")

# --------------------------
# Config
# --------------------------
MODEL_NAME   = os.getenv("STT_MODEL", "base.en")
DEVICE       = os.getenv("STT_DEVICE", "cpu")
COMPUTE_TYPE = os.getenv("STT_COMPUTE", "int8")
LANGUAGE     = os.getenv("STT_LANGUAGE", "")
VAD_FILTER   = os.getenv("STT_VAD", "1") == "1"
ALLOW_ORIGIN_REGEX = os.getenv("STT_ALLOW_ORIGIN_REGEX", ".*")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUNO_API_KEY = os.getenv("SUNO_API_KEY")

# --------------------------
# Logging
# --------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("stt")

# --------------------------
# App & CORS
# --------------------------
app = FastAPI(title="Speech-to-Text Backend (Faster-Whisper)")
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --------------------------
# Utilities
# --------------------------
_MODEL: Optional[WhisperModel] = None

def ffmpeg_ok() -> bool:
    try:
        out = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        return out.returncode == 0
    except Exception:
        return False

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
# Voice Emotion Stub (replace with ML model later)
# --------------------------
def get_emotion_data(audio_path: str) -> dict:
    """
    Placeholder: Return valence/arousal/dominance from audio.
    Replace with your real neural network model or API.
    """
    return {"valence": 0.7, "arousal": 0.4, "dominance": 0.6}

# --------------------------
# Suno Client
# --------------------------
def generate_music_from_prompt(prompt: dict) -> str:
    """
    Calls Suno API and returns URL of generated audio.
    """
    url = "https://api.suno.ai/v1/generate"
    headers = {
        "Authorization": f"Bearer {SUNO_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=prompt)
    response.raise_for_status()
    data = response.json()
    return data.get("audioUrl") or data.get("audio")

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

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    log.info(f"Incoming file: name='{audio.filename}' type='{audio.content_type}'")

    # Save audio to temp file
    suffix = Path(audio.filename or "").suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp_path = Path(tmp.name)
        file_bytes = await audio.read()
        if not file_bytes:
            raise friendly_error("Uploaded file is empty.", 400)
        tmp.write(file_bytes)

    try:
        if not ffmpeg_ok():
            raise friendly_error("ffmpeg is not installed or not on PATH.", 500)

        model = get_model()
        lang = LANGUAGE if LANGUAGE.strip() else None

        log.info(f"Transcribing '{tmp_path.name}' (lang={lang or 'auto'}, vad={VAD_FILTER})")
        segments, info = model.transcribe(
            str(tmp_path),
            vad_filter=VAD_FILTER,
            word_timestamps=True,
            language=lang,
            beam_size=5
        )

        # Aggregate text
        transcript = " ".join(seg.text.strip() for seg in segments if seg.text)

        # Voice emotion analysis
        emotion = get_emotion_data(str(tmp_path))

        # Build LLM prompt
        llm_prompt = f"""
You are an empathetic assistant for a mental health journaling app.
The user has recorded this journal entry:

"{transcript}"

The detected voice emotions are:
Valence: {emotion['valence']}, Arousal: {emotion['arousal']}, Dominance: {emotion['dominance']}

Do two things:
1) Generate a 1-3 sentence comforting reply.
2) Generate a Suno music prompt object internally (do NOT return JSON to the user, just use it to generate music).

Respond with a JSON containing only:
{{
    "response": "<comforting reply>",
    "musicPrompt": {{
        "prompt": "<description for Suno>",
        "style": "Classical",
        "title": "Peaceful Piano Meditation",
        "customMode": true,
        "instrumental": true,
        "model": "V3_5",
        "negativeTags": "Heavy Metal, Upbeat Drums",
        "vocalGender": "m",
        "styleWeight": 0.65,
        "weirdnessConstraint": 0.65,
        "audioWeight": 0.65,
        "callBackUrl": "https://api.example.com/callback"
    }}
}}
"""

        # Call Anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        completion = client.completions.create(
            model="claude-3",
            prompt=llm_prompt,
            max_tokens_to_sample=500,
            temperature=0.7
        )
        llm_output = completion.completion
        data = json.loads(llm_output)

        # Generate music
        audio_url = generate_music_from_prompt(data["musicPrompt"])

        # Aggregate segments/words for return
        out_segments = [
            {
                "id": seg.id,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text,
                "avg_logprob": seg.avg_logprob,
                "no_speech_prob": getattr(seg, "no_speech_prob", None),
                "compression_ratio": getattr(seg, "compression_ratio", None)
            }
            for seg in segments
        ]
        out_words = [
            {"word": w.word, "start": w.start, "end": w.end, "prob": w.probability}
            for seg in segments for w in getattr(seg, "words", [])
        ]

        return JSONResponse({
            "engine": "faster-whisper",
            "model": MODEL_NAME,
            "device": DEVICE,
            "compute_type": COMPUTE_TYPE,
            "duration": getattr(info, "duration", None),
            "language": getattr(info, "language", None),
            "text": data["response"],
            "audio_url": audio_url,
            "segments": out_segments,
            "words": out_words
        })

    except HTTPException:
        raise
    except Exception as e:
        log.error("Transcription failed:\n" + traceback.format_exc())
        raise friendly_error(f"Transcription failed: {e}", 500)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass
