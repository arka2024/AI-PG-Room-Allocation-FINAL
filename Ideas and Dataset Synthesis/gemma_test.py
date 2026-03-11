import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemma-3-27b-it"

URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

headers = {
    "Content-Type": "application/json"
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": "Say hello in one short sentence."}
            ]
        }
    ]
}

response = requests.post(URL, headers=headers, json=payload)

print("Status Code:", response.status_code)
print(json.dumps(response.json(), indent=2))