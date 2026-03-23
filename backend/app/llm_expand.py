import requests
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
LLM_MODEL = os.getenv("LLM_MODEL")


def expand_skill(skill: str):

    prompt = f"""
You are an expert HR recruiter.

Given the skill: "{skill}"

Generate 10 closely related professional skills.
Return only a comma-separated list.
No explanations.
"""

    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    # Debug output
    print(response.json())

    data = response.json()

    if "response" not in data:
        raise Exception(f"Ollama error: {data}")

    text = data["response"]

    return [s.strip() for s in text.split(",") if s.strip()]