
from langchain.text_splitter import MarkdownHeaderTextSplitter
from utils.sanitizer import sanitize_id

def chunk_markdown_by_headers(markdown_text, source_name):
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[
        ("#", "h1"), ("##", "h2"), ("###", "h3")
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