# backend/app/apyhub_client.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("APYHUB_API_KEY")

def get_related_jobs(job_title: str):

    url = "https://api.apyhub.com/sharpapi/api/v1/hr/related_job_positions"

    headers = {
        "Content-Type": "application/json",
        "apiKey": API_KEY
    }

    payload = {
        "job_title": job_title
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"ApyHub error: {response.text}")

    return response.json()