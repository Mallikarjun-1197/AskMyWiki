🧠 Ask My Wiki
Ask My Wiki is a Streamlit-powered Retrieval-Augmented Generation (RAG) assistant that answers domain-specific questions over internal wiki content. It combines semantic chunking, fingerprint-based caching, Azure AI Search, and GPT summarization to deliver fast, accurate, and transparent responses.

🚀 Features
- 🔍 Semantic Chunking: Breaks wiki pages into topic-aware chunks with rich metadata.
- 🧠 GPT Summarization: Synthesizes retrieved content into clean, human-readable answers.
- 🧬 Fingerprint-Based Caching: Avoids redundant indexing and embedding.
- 📦 Azure AI Search Integration: Retrieves relevant chunks using vector similarity.
- 💬 Multi-Turn Chat UI: Built with Streamlit’s chat_input and chat_message for a conversational experience.
- 🔎 Transparent Retrieval: Users can inspect the exact chunks used to generate each answer.

📽️ Demo
Watch the full walkthrough here: 
<iframe src="https://www.loom.com/embed/ae078434a8ce4c399eab9481a91b9fb3" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen width="100%" height="400"></iframe>

🛠️ Tech Stack
UI: Streamlit
Agent Logic: Custom WikiAgent
Embedding: Azure OpenAI
Search: Azure AI Search
Caching: Azure Table Storage
Summarization: GPT-based synthesis
Logging: Smart logger with env-based levels
Chunking: Semantic chunker with metadata extraction
Fingerprinting: Content-based deduplication and sync control

🧰 Setup
1. Clone the repo
git clone https://github.com/Mallikarjun-1197/AskMyWiki.git
cd AskMyWiki

2. Install dependencies
pip install -r requirements.txt

3. Configure environment
Create a .env file based on .env.example:
AI_SEARCH_KEY=your-key-here
AI_SEARCH_ENDPOINT=https://your-search-endpoint
AI_SEARCH_API_VERSION=2023-07-01
LOG_LEVEL=INFO

4. Run the app
streamlit run app.py

🛡️ Security
- .env is excluded via .gitignore
- Secrets are never committed
- .env.example provided for safe replication

🙌 Author
Built by Mallik..






