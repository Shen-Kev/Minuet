import os
import random
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Minuet Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

SUNO_FOLDER = os.path.join(os.path.dirname(__file__), "SUNO_tunes")

@app.get("/play_random")
def play_random():
    # List only mp3 files
    mp3_files = [f for f in os.listdir(SUNO_FOLDER) if f.lower().endswith(".mp3")]
    if not mp3_files:
        return {"error": "No MP3 files found in SUNO_tunes"}

    # Pick a random file
    random_mp3 = random.choice(mp3_files)

    # Full path
    mp3_path = os.path.join(SUNO_FOLDER, random_mp3)

    # Return as FileResponse so frontend can fetch & play
    return FileResponse(
        mp3_path,
        media_type="audio/mpeg",
        filename=random_mp3  # preserves original name with spaces
    )
Frontend Fetch (HTML/JS)
html
Copy code
<button id="playBtn">Play Random Tune</button>
<audio id="audioPlayer" controls></audio>

<script>
const playBtn = document.getElementById("playBtn");
const audioPlayer = document.getElementById("audioPlayer");

playBtn.addEventListener("click", async () => {
    try {
        const response = await fetch("/play_random");
        if (!response.ok) throw new Error("Failed to fetch MP3");

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        audioPlayer.src = url;
        audioPlayer.play();
    } catch (err) {
        console.error(err);
        alert("Could not load MP3. Check that SUNO_tunes folder has MP3s.");
    }
});
</script>
