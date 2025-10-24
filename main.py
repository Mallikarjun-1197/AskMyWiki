import os
from gpt.gpt_client import call_gpt
from agent.wiki_agent import WikiAgent
from utils.formatter import build_prompt
from search.searcher import search
from search.indexer import create_index
from chunking.fetcher import fetch_page_and_subpages
from embedding.embedder import embed_text
from fingerprint.store import TableFingerprintStore
import requests
import json
import pdb
from embedding.embedder import embed_text
from dotenv import load_dotenv
from customlogging.logger import setup_logger

load_dotenv()
logger = setup_logger()




FORCE_FULL_SYNC = os.getenv("FORCE_FULL_SYNC", "false").lower() == "true"


def extract_title_like_line(text):
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith(("the ", "this ", "these ", "those ", "it ")):
            continue
        if 5 < len(line) < 80 and line[-1] not in ".!?":
            return line
    return None

def infer_section(chunk):
    section=  (
        chunk.get("section") or
        chunk["metadata"].get("h1") or
        chunk["metadata"].get("h2") or
        chunk["metadata"].get("h3") or
        extract_title_like_line(chunk["text"]) or
        "Untitled Section"
    )
    if section.lower() == "untitled section" or section == " " or section == "":
        print(f"{chunk} has no section ")
    return section

def upload_chunks(chunks):
    fp_store = TableFingerprintStore()
    upload_payload = []

    for chunk in chunks:
        chunk_id = chunk["id"]
        filename = chunk.get("filename") or "Untitled Page"
        section = infer_section(chunk)
        text = chunk["text"]

        fingerprint = fp_store.compute_fingerprint(text, section, filename, chunk.get("url", ""))
        existing_fp = fp_store.get(chunk_id, filename)

        if existing_fp != fingerprint:
            if section.lower() in ["unknown", "untitled section"]:
                print(f"⚠️ Section Unknow for {text[:30]}")
            logger.smart_log(f"🆕 New or changed chunk → uploading: {section}")
            # print(f"🆕 New or changed chunk → uploading: {section}")
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
            fp_store.store_fp(chunk_id, fingerprint, section, filename)
        else:
             logger.smart_log(f"✅ Chunk unchanged → skipping: {section}")
            # print(f"✅ Chunk unchanged → skipping: {section}")

    fp_store.save()

    if upload_payload:
        headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv("AI_SEARCH_KEY")
        }
        upload_url = f"{os.getenv('AI_SEARCH_ENDPOINT')}/indexes/ragwikiindex/docs/index?api-version={os.getenv('AI_SEARCH_API_VERSION')}"
        response = requests.post(upload_url, headers=headers, json={"value": upload_payload})
        if response.status_code == 200:
            print("✅ Chunks uploaded successfully.")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)


if __name__ == "__main__":
    if FORCE_FULL_SYNC:
        print("🔁 Rechunking and reindexing wiki content...")
        create_index()
        chunks = fetch_page_and_subpages("/")
        upload_chunks(chunks)

    user_input = input("What do you want to know about? ")
    agent = WikiAgent(lambda prompt: call_gpt(prompt))
    results = agent.run(user_input)

    all_chunks = [chunk for _, chunks in results for chunk in chunks]
    prompt = build_prompt(user_input, all_chunks)
    response = call_gpt(prompt)