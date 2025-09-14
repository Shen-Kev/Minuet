# testsuno_status.py
import os
import requests

# --------------------------
# Load Suno API key
# --------------------------
SUNO_API_KEY = os.getenv("SUNO_API_KEY")

if not SUNO_API_KEY:
    raise ValueError("Please set your SUNO_API_KEY environment variable.")

# --------------------------
# API request
# --------------------------
url = "https://api.suno.ai/v1/status"
headers = {
    "Authorization": f"Bearer {SUNO_API_KEY}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raises HTTPError if status != 200
    print("Suno API status response:")
    print(response.text)
except requests.exceptions.HTTPError as http_err:
    print(f"HTTP error occurred: {http_err}")
except requests.exceptions.RequestException as err:
    print(f"Error occurred: {err}")
