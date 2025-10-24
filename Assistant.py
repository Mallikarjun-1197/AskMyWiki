from logger import get_logger
log = get_logger("Assistant")

import os
import json
import requests
import base64
import logging
from dotenv import load_dotenv
from langchain.text_splitter import MarkdownHeaderTextSplitter
from openai import AzureOpenAI
from azure.data.tables import TableServiceClient
from FingerprintStore import FingerprintStore
import hashlib
from agent.planner import Planner
from agent.wiki_agent import WikiAgent

# ─────────────────────────────────────────────────────────────
# ✅ Setup & Configuration
# ─────────────────────────────────────────────────────────────

load_dotenv()

fp_store = FingerprintStore()
ORG = os.getenv("organization")
PROJECT = os.getenv("project")
WIKI_ID = os.getenv("wiki_id")
PAT = os.getenv("pat")
AI_SEARCH_ENDPOINT = os.getenv("AI_SEARCH_ENDPOINT")
AI_SEARCH_KEY = os.getenv("AI_SEARCH_KEY")
AI_SEARCH_API_VERSION = os.getenv("AI_SEARCH_API_VERSION")
TEXT_EMBEDDING_MODEL = os.getenv("TEXT_EMBEDDING_MODEL")
EMBEDDING_MODEL_URL = os.getenv("EMBEDDING_MODEL_URL")
EMBEDDING_MODEL_KEY = os.getenv("EMBEDDING_MODEL_KEY")
GPT_4o_URL = os.getenv("GPT_4o_URL")
GPT_4o_API_key = os.getenv("GPT_4o_API_key")
GPT_4o_Deployment_Name= os.getenv("GPT_4o_Deployment_Name")
GPT_4o_Version = os.getenv("GPT_4o_Version")
FINGERPRINT_CACHE = os.getenv("FINGERPRINT_CACHE")
FORCE_FULL_SYNC = os.getenv("FORCE_FULL_SYNC", "false").lower() == "true"


if not all([ORG, PROJECT, WIKI_ID, PAT]):
    raise ValueError("Missing required environment variables. Check .env file.")

BASE_URL = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wiki/wikis/{WIKI_ID}/pages"
HEADERS = {
    "Authorization": f"Basic {base64.b64encode(f':{PAT}'.encode()).decode()}"
}

# logging.basicConfig(level=logging.ERROR, format="🔧 %(message)s")
logging.basicConfig(level=logging.ERROR, format="❌ %(levelname)s: %(message)s")

import re

def sanitize_id(value):
    # Replace forbidden characters with underscore
    value = re.sub(r'[^A-Za-z0-9_\-=]', '_', value)
    value = re.sub(r'^_+', '', value)
    return value


def fingerprint(text):
    return hashlib.sha256(text.strip().encode('utf-8')).hexdigest()

def load_fingerprint_cache():
    if FORCE_FULL_SYNC and os.path.exists(FINGERPRINT_CACHE):
        os.remove(FINGERPRINT_CACHE)
        return set()  # Full sync: treat all chunks as new

    if os.path.exists(FINGERPRINT_CACHE):
        with open(FINGERPRINT_CACHE, "r") as f:
            return set(json.load(f))  # Incremental sync: load existing fingerprints

    return set()  # No cache file yet


def save_fingerprint_cache(fingerprints):
    with open(FINGERPRINT_CACHE, "w") as f:
        json.dump(list(fingerprints), f)


# ─────────────────────────────────────────────────────────────
# 🧠 Markdown Chunking
# ─────────────────────────────────────────────────────────────

def chunk_markdown_by_headers(markdown_text, source_name):
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3")
    ])
    docs = splitter.split_text(markdown_text)
   
    chunks = []
    for i, doc in enumerate(docs):
        chunks.append({
            "id": sanitize_id(f"{source_name}-{i}"),
            "text": doc.page_content.strip(),
            "source": source_name,
            "metadata": doc.metadata
        })
    return chunks

# ─────────────────────────────────────────────────────────────
# 📦 Fetch SubPages of a page
# ─────────────────────────────────────────────────────────────

def fetch_page_and_subpages(page_path):
    page_url = (
        f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wiki/wikis/{WIKI_ID}/pages"
        f"?path={page_path}&recursionLevel=full&includeContent=True&api-version=7.1"
    )

    try:
        response = requests.get(page_url, headers=HEADERS)
        response.raise_for_status()
        page_data = response.json()
    except Exception as e:
        logging.warning(f"Failed to fetch page {page_path}: {e}")
        return []

    markdown = page_data.get("content", "")
    page_id = page_data.get("id")
    source_name = page_data.get("path", "").strip("/").replace(" ", "-")
    wiki_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_wiki/wikis/{WIKI_ID}/{page_id}/{source_name}"
    chunks = chunk_markdown_by_headers(markdown, source_name)

    for chunk in chunks:
        chunk["section"] = chunk["metadata"].get("h1", "Unknown")
        chunk["filename"] = source_name
        chunk["url"] = wiki_url

    all_chunks = chunks

    for subpage in page_data.get("subPages", []):
        sub_chunks = fetch_page_and_subpages(subpage.get("path", ""))
        all_chunks.extend(sub_chunks)

    return all_chunks


# ─────────────────────────────────────────────────────────────
# 📦 Fetch Wiki Pages
# ─────────────────────────────────────────────────────────────

def fetch_all_pages():
    base_path_url = (
        f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wiki/wikis/{WIKI_ID}/pages"
        "?path=/&recursionLevel=full&includeContent=True&api-version=7.1"
    )

    try:
        response = requests.get(base_path_url, headers=HEADERS)
        response.raise_for_status()
        root = response.json()
    except Exception as e:
        logging.error(f"Failed to fetch root wiki page list: {e}")
        return []

    all_chunks = []

    for page in root.get("subPages", []):
        all_chunks.extend(fetch_page_and_subpages(page.get("path", "")))

        # logging.info(f"✅ Chunked: {source_name} → {len(chunks)} chunks")
    print("Chunking completed ✅✅")
    return all_chunks

# ─────────────────────────────────────────────────────────────
# 📦 Creating an index in Azure AI Search
# ─────────────────────────────────────────────────────────────

def create_index():
    with open("indexConfig.json",'r') as config:
        index_schema = json.load(config)
        index_name = index_schema.get("name")
        url = f"{AI_SEARCH_ENDPOINT}/indexes/{index_name}?api-version={AI_SEARCH_API_VERSION}"
        headers = {
            "Content-Type":"application/json",
            "api-key": AI_SEARCH_KEY
        }
        created_index = requests.put(url, headers= headers, json= index_schema)
        print(f"🔧 Status Code: {created_index.status_code}")
        try:
            print(json.dumps(created_index.json(), indent=2))
        except json.JSONDecodeError:
            print("⚠️ Response is not JSON. Raw text:")
            print(created_index.text)

# ─────────────────────────────────────────────────────────────
# 🚀 Main Execution
# ─────────────────────────────────────────────────────────────

def embed_text(text):
    headers = {
        "Content-Type" : "application/json",
        "api-key" : EMBEDDING_MODEL_KEY
    }
    input = { "input": text }
    response = requests.post(EMBEDDING_MODEL_URL , headers= headers , json = input)
    return response.json()["data"][0]["embedding"]

def upload_chunks(chunks):
    fp_store = FingerprintStore()
    upload_payload = []
    delete_payload = []

    for chunk in chunks:
        chunk_id = chunk["id"]
        filename = chunk.get("filename", "Unknown")
        section = chunk.get("section", "Unknown")
        text = chunk["text"]

        fingerprint = fp_store.compute_fingerprint(
            text=chunk["text"],
            section=chunk.get("section", ""),
            filename=chunk.get("filename", ""),
            url=chunk.get("url", "")
        )
        existing_fp = fp_store.get(chunk_id, filename)

        if existing_fp != fingerprint:
            print(f"🆕 New or changed chunk → uploading: {section}")
            embedding = embed_text(text)
            doc = {
                "@search.action": "upload",
                "id": chunk_id,
                "text": text,
                "source": chunk["source"],
                "metadata": json.dumps(chunk["metadata"], sort_keys=True),
                "embedding": embedding,
                "fingerprint": fingerprint,
                "section": section,
                "filename": filename,
                "url": chunk.get("url", "")
            }
            upload_payload.append(doc)
            fp_store.store(chunk_id, fingerprint, section, filename)
        else:
            print(f"✅ Chunk unchanged → skipping: {section}")

    # 🚀 Upload new chunks
    if upload_payload:
        headers = {
            "Content-Type": "application/json",
            "api-key": AI_SEARCH_KEY
        }
        upload_url = f"{AI_SEARCH_ENDPOINT}/indexes/ragwikiindex/docs/index?api-version={AI_SEARCH_API_VERSION}"
        response = requests.post(upload_url, headers=headers, json={"value": upload_payload})
        if response.status_code == 200:
            logging.info("✅ Chunks uploaded successfully.")
        else:
            logging.error(f"❌ Upload failed: {response.status_code}")
            logging.error(response.text)


def search(user_query):
    url = f"{AI_SEARCH_ENDPOINT}/indexes/ragwikiindex/docs/search.post.search?api-version={AI_SEARCH_API_VERSION}"
    usr_input_embedding = embed_text(user_query)
    headers = {
        "Content-Type" : "application/json",
        "api-key" : AI_SEARCH_KEY
    }
    payload = {
        "search": user_query,
        "vectorQueries": [{
            "kind":"vector",
            "vector": usr_input_embedding,
            "fields" : "embedding",
            "k": 10,
        }]
    }
    # print(url)
    # print(payload)
    resposne = requests.post(url= url, headers= headers , json= payload)
    results = resposne.json().get('value',[])
    for result in results:
        returned_resp = {
            "text": result.get("text"),
            "source": result.get("source"),
            "metadata":result.get("source")
        }
        # print(f"🤖🤖 Reponse from search : {json.dumps(returned_resp,indent= 3)}")
    return results

def callGpt(prompt):
    client = AzureOpenAI(
        azure_endpoint= GPT_4o_URL,
        api_key= GPT_4o_API_key ,
        api_version= GPT_4o_Version
    )
    response_stream = client.chat.completions.create(
        messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant that answers based only on the provided context.If a URL is present, include it in your answer for traceability.",
        },
        {
            "role": "user",
            "content": prompt,
        }
    ],
    max_tokens=4096,
    temperature=1.0,
    top_p=1.0,
    model=GPT_4o_Deployment_Name,
    stream = True
    )
    # return response.choices[0].message.content
    full_response = ""

    for chunk in response_stream:
        if not chunk.choices or not chunk.choices[0].delta:
            continue  # Skip empty or malformed chunks

        delta = chunk.choices[0].delta
        if delta.content:
            print(delta.content, end="", flush=True)
            full_response += delta.content
    return full_response

    
def format_chunks(chunks):
    return "\n\n".join(
        f"Chunk {i+1} (source: {doc['source']}, section: {doc.get('section')}):\n"
        f"{doc['text']}\n"
        f"🔗 [View Source]({doc.get('url')})"
        for i, doc in enumerate(chunks)
    )


def build_prompt(query, results):
    context = format_chunks(results)
    return f"""You are an assistant answering based only on the context below.

{context}

Question:
{query}

Answer clearly and concisely. If the context is insufficient, say so explicitly.
If tools, libraries, or implementation details are mentioned in the context, include them in your answer.
Format your response using Markdown.
If a URL is provided, include all the URLS at the end of your response in a more user friendly way

"""
#  If the context is insufficient, say so explicitly.



if __name__ == "__main__":
    if FORCE_FULL_SYNC == True:
        create_index()
        chunks = fetch_all_pages()
        upload_chunks(chunks=chunks)   
    user_input = input("What do you want to know about ?? ")
    search_response = search(user_input)
    prompt = build_prompt(user_input,search_response)
    airesponse = callGpt(prompt)

    agent = WikiAgent(lambda _prompt : callGpt(_prompt))
    results = agent.run(user_input)
    