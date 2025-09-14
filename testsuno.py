import os
import requests
import json

SUNO_API_KEY = os.getenv("SUNO_API_KEY")

prompt = {
    "prompt": "Generate a short relaxing piano track with water sounds.",
    "style": "Classical",
    "title": "Test Soothing Track",
    "customMode": True,
    "instrumental": True,
    "model": "V3_5",
    "negativeTags": "Heavy Metal, Upbeat Drums",
    "vocalGender": "m",
    "styleWeight": 0.65,
    "weirdnessConstraint": 0.65,
    "audioWeight": 0.65,
    "callBackUrl": "https://api.example.com/callback"
}

url = "https://api.suno.ai/v1/generate"
headers = {
    "Authorization": f"Bearer {SUNO_API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers, json=prompt)
response.raise_for_status()
data = response.json()

print("SUNO responded with audio URL:", data.get("audioUrl") or data.get("audio"))

# Optional: download the MP3 locally
audio_url = data.get("audioUrl") or data.get("audio")
if audio_url:
    r = requests.get(audio_url)
    with open("test_suno.mp3", "wb") as f:
        f.write(r.content)
    print("MP3 downloaded as test_suno.mp3")
