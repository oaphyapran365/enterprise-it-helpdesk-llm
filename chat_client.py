# file: chat_client.py
# Simple terminal chat client for the local Ollama /api/chat endpoint.
# Usage:
#   1) Start Ollama server:  ollama serve
#   2) Run this:            python chat_client.py
#   3) Type your questions. Type /reset to clear, /quit to exit.

import json
import requests

URL = "http://localhost:11434/api/chat"
MODEL = "helpdesk"

def ollama_chat(messages, model=MODEL, temperature=0.2, stream=True, timeout=600):
    payload = {
        "model": model,
        "messages": messages,
        "options": {"temperature": temperature},
        "stream": stream,
    }
    with requests.post(URL, json=payload, stream=stream, timeout=timeout) as r:
        r.raise_for_status()

        if not stream:
            data = r.json()
            return data["message"]["content"]

        full = ""
        for line in r.iter_lines():
            if not line:
                continue
            obj = json.loads(line.decode("utf-8"))
            chunk = obj.get("message", {}).get("content", "")
            if chunk:
                print(chunk, end="", flush=True)
                full += chunk
            if obj.get("done"):
                break
        print()
        return full

def main():
    print("IT Helpdesk Chatbot (Ollama)")
    print("Commands: /reset  /quit")
    history = []  # model already has SYSTEM prompt baked in via Helpdesk.Modelfile

    while True:
        user = input("\nYou: ").strip()
        if not user:
            continue
        if user.lower() in {"/quit", "/exit"}:
            break
        if user.lower() == "/reset":
            history = []
            print("History cleared.")
            continue

        history.append({"role": "user", "content": user})
        print("Bot: ", end="", flush=True)
        answer = ollama_chat(history, stream=True)
        history.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    main()
