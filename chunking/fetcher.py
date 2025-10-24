
import requests
import base64
import os
import pdb
from chunking.chunker import chunk_markdown_by_headers
from dotenv import load_dotenv

load_dotenv()


ORG = os.getenv("organization")
PROJECT = os.getenv("project")
WIKI_ID = os.getenv("wiki_id")
PAT = os.getenv("pat")

HEADERS = {
    "Authorization": f"Basic {base64.b64encode(f':{PAT}'.encode()).decode()}",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"

}
def infer_section(chunk):
    return (
        chunk["metadata"].get("h1") or
        chunk["metadata"].get("h2") or
        chunk["metadata"].get("h3") or
        extract_title_like_line(chunk["text"]) or
        "Untitled Section"
    )

def extract_title_like_line(text):
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # Skip generic starters
        if line.lower().startswith(("the ", "this ", "these ", "those ", "it ")):
            continue
        # Return if it's short and title-like
        if 5 < len(line) < 80 and line[-1] not in ".!?":
            return line
    return None

def fetch_page_and_subpages(page_path):
    url = f"https://dev.azure.com/{ORG}/{PROJECT}/_apis/wiki/wikis/{WIKI_ID}/pages?path={page_path}&recursionLevel=full&includeContent=True&api-version=7.1"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    page_data = response.json()

    markdown = page_data.get("content", "")
    page_id = page_data.get("id")
    source_name = page_data.get("path", "").strip("/").replace(" ", "-")
    wiki_url = f"https://dev.azure.com/{ORG}/{PROJECT}/_wiki/wikis/{WIKI_ID}/{page_id}/{source_name}"

    chunks = chunk_markdown_by_headers(markdown, source_name)
    for chunk in chunks:
        section = infer_section(chunk)
        chunk["section"] = section
        chunk["filename"] = source_name or "Untitled Page"
        chunk["url"] = wiki_url

    all_chunks = chunks
    for subpage in page_data.get("subPages", []):
        all_chunks.extend(fetch_page_and_subpages(subpage.get("path", "")))

    return all_chunks