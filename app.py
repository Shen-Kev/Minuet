# app.py
# FastAPI backend for browser-recorded audio -> text
# Uses Faster-Whisper, Anthropic Claude, and Suno API

import os
import tempfile
import logging
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import requests
import anthropic
import subprocess

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from faster_whisper import WhisperModel

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
# FastAPI app & CORS
# --------------------------
app = FastAPI(title="Minuet STT Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOW_ORIGIN_REGEX,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --------------------------
# Utilities
# ------------
