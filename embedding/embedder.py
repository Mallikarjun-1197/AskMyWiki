
import requests
import os
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL_URL = os.getenv("EMBEDDING_MODEL_URL")
EMBEDDING_MODEL_KEY = os.getenv("EMBEDDING_MODEL_KEY")

def embed_text(text):
    headers = {
        "Content-Type": "application/json",
        "api-key": EMBEDDING_MODEL_KEY
    }
    response = requests.post(EMBEDDING_MODEL_URL, headers=headers, json={"input": text})
    return response.json()["data"][0]["embedding"]