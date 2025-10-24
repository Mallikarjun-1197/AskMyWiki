import requests
import os
from embedding.embedder import embed_text

AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
AI_SEARCH_KEY = os.getenv("AI_SEARCH_KEY")
AI_SEARCH_API_VERSION = os.getenv("AI_SEARCH_API_VERSION")

def search(user_query):
    url = f"{AI_SEARCH_ENDPOINT}/indexes/ragwikiindex/docs/search.post.search?api-version={AI_SEARCH_API_VERSION}"
    headers = {
        "Content-Type": "application/json",
        "api-key": AI_SEARCH_KEY
    }
    embedding = embed_text(user_query)
    payload = {
        "search": user_query,
        "vectorQueries": [{
            "kind": "vector",
            "vector": embedding,
            "fields": "embedding",
            "k": 10
        }]
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json().get("value", [])