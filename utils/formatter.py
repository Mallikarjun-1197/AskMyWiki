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
Format your response using Markdown.
Include all URLs at the end of your response in a user-friendly way.
"""