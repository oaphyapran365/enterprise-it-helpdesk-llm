# file: app.py
# Streamlit web UI for the local Ollama helpdesk chatbot.
#
# Run:
#   pip install -r requirements.txt
#   streamlit run app.py

import json
import streamlit as st
import requests
from datetime import datetime

URL = "http://localhost:11434/api/chat"

st.set_page_config(page_title="IT Helpdesk Chatbot", page_icon="💬")
st.title("💬 IT Helpdesk Chatbot (Ollama)")

# Sidebar controls
model = st.sidebar.text_input("Model name", value="helpdesk")
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
st.sidebar.caption("Tip: 0.1–0.3 gives consistent, checklist-style answers.")

if st.sidebar.button("Clear chat"):
    st.session_state.history = []
    st.rerun()

# Store conversation history in session
if "history" not in st.session_state:
    # The model already has a SYSTEM prompt in Helpdesk.Modelfile
    st.session_state.history = []

# Show previous messages
for m in st.session_state.history:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

def stream_ollama(messages):
    payload = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature},
        "stream": True,
    }
    with requests.post(URL, json=payload, stream=True, timeout=600) as r:
        r.raise_for_status()
        full = ""
        for line in r.iter_lines():
            if not line:
                continue
            obj = json.loads(line.decode("utf-8"))
            chunk = obj.get("message", {}).get("content", "")
            if chunk:
                full += chunk
                yield full
            if obj.get("done"):
                break

user_msg = st.chat_input("Describe your IT issue...")
if user_msg:
    # Add user message
    st.session_state.history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # Generate assistant response (streaming)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        final = ""
        try:
            for partial in stream_ollama(st.session_state.history):
                final = partial
                placeholder.markdown(final)
        except Exception as e:
            final = f"Error talking to Ollama: {e}"
            placeholder.markdown(final)

    st.session_state.history.append({"role": "assistant", "content": final})

# Export transcript
st.divider()
st.subheader("Export (for your report)")

def transcript_markdown():
    lines = []
    lines.append("# Chat Transcript")
    lines.append(f"- Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"- Model: {model}")
    lines.append(f"- Temperature: {temperature}")
    lines.append("")
    for m in st.session_state.history:
        role = m["role"].capitalize()
        lines.append(f"## {role}")
        lines.append(m["content"])
        lines.append("")
    return "\n".join(lines)

md = transcript_markdown()
st.download_button(
    label="Download transcript (Markdown)",
    data=md.encode("utf-8"),
    file_name="chat_transcript.md",
    mime="text/markdown",
)
st.caption("You can paste this into Word or include screenshots of key Q/A pairs.")
