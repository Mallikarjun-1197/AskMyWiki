import json
import os
import requests

def create_index():
    AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
    AI_SEARCH_API_VERSION = os.getenv("AI_SEARCH_API_VERSION")
    AI_SEARCH_KEY = os.getenv("AI_SEARCH_KEY")
    config_path = os.path.join(os.path.dirname(__file__), "indexConfig.json")
    with open(config_path, "r") as config:
        index_schema = json.load(config)
        index_name = index_schema.get("name")
        url = f"{AI_SEARCH_ENDPOINT}/indexes/{index_name}?api-version={AI_SEARCH_API_VERSION}"
        headers = {
            "Content-Type": "application/json",
            "api-key": AI_SEARCH_KEY
        }
        response = requests.put(url, headers=headers, json=index_schema)
        print(f"🔧 Status Code: {response.status_code}")
        try:
            print(json.dumps(response.json(), indent=2))
        except json.JSONDecodeError:
            print("⚠️ Response is not JSON. Raw text:")
            print(response.text)