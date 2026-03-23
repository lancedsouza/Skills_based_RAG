import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Strip any trailing slashes from the URL automatically
OLLAMA_URL = os.getenv("OLLAMA_URL").rstrip("/")
MODEL = os.getenv("EMBED_MODEL")

def get_embedding(text: str):
    # Try the modern endpoint first (standard in 2026)
    url = f"{OLLAMA_URL}/api/embed"
    payload = {
        "model": MODEL,
        "input": text  # New API uses 'input'
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        
        # If /api/embed fails, fall back to legacy /api/embeddings
        if response.status_code == 404:
            url = f"{OLLAMA_URL}/api/embeddings"
            payload = {"model": MODEL, "prompt": text} # Legacy uses 'prompt'
            response = requests.post(url, json=payload, timeout=30)

        response.raise_for_status()
        data = response.json()

        # Handle the different response shapes
        if "embeddings" in data:
            return data["embeddings"][0]  # From /api/embed
        return data["embedding"]          # From /api/embeddings

    except Exception as e:
        # This will print in your 'docker-compose logs -f backend'
        print(f"CRITICAL ERROR: Failed to get embedding from {url}")
        print(f"PAYLOAD USED: {payload}")
        raise RuntimeError(f"Embedding failed: {e}")