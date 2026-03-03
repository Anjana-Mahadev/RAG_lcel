import streamlit as st
import requests

BACKEND_URL = "http://localhost:8000/query"

st.set_page_config(page_title="RAG Chatbot", layout="wide")

st.title("📚 RAG Chatbot")
st.markdown("Ask questions from your uploaded PDFs.")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Ask your question..."):
    # Save user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call backend
    response = requests.post(
        BACKEND_URL,
        json={"question": prompt}
    )

    if response.status_code == 200:
        answer = response.json()["answer"]
    else:
        answer = "Error contacting backend."

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)