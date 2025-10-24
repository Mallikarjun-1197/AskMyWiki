import streamlit as st
from main import WikiAgent, call_gpt, build_prompt
from dotenv import load_dotenv

load_dotenv()
agent = WikiAgent(lambda prompt: call_gpt(prompt))

st.set_page_config(page_title="Ask My Wiki", layout="centered")
st.title("🧠 Ask My Wiki")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Clear chat button (sidebar or top of page)
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat_history.clear()
    st.rerun()  # Refresh the app to clear input box too


# Display chat history
for q, r in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        st.markdown(r)

# Chat input box (bottom of screen)
query = st.chat_input("Ask your wiki...")

if query:
    with st.chat_message("user"):
        st.markdown(query)
        
    with st.spinner("Thinking..."):
        results = agent.run(query)
        all_chunks = [chunk for _, chunks in results for chunk in chunks]
        prompt = build_prompt(query, all_chunks)
        response = call_gpt(prompt)

    with st.chat_message("assistant"):
        st.markdown(response)
    # 🔍 Show retrieved chunks
    with st.expander("🔍 Retrieved Chunks"):
        for chunk in all_chunks:
            section = chunk.get("section", "Unknown Section")
            st.markdown(f"**{section}**")
            st.write(chunk["text"][:300] + "...")

    # Save to history
    st.session_state.chat_history.append((query, response))