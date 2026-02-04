# file: run_tests.py
# Runs 6–8 sample IT support questions and saves outputs for your report.
#
# Usage:
#   1) Start Ollama:            ollama serve
#   2) Ensure model exists:     ollama create helpdesk -f Helpdesk.Modelfile
#   3) Run tests:              python run_tests.py
#
# Outputs:
#   outputs/test_outputs.jsonl   (1 JSON object per line)
#   outputs/test_outputs.md      (report-friendly markdown)
#   outputs/eval_template.csv    (blank scoring sheet you can fill)

import csv
import json
import os
from datetime import datetime
import requests

URL = "http://localhost:11434/api/chat"
MODEL = "helpdesk"

QUESTIONS = [
    "My email isn’t sending. It stays in Outbox. Help!",
    "I forgot my password and my account is locked. What should I do?",
    "Wi‑Fi connects but the internet doesn’t work on my laptop.",
    "My printer shows 'offline' and won’t print.",
    "VPN says authentication failed. I need access to campus resources.",
    "Teams/Zoom microphone not working in meetings.",
    "I clicked a suspicious link in an email. What should I do now?",
    "My computer is very slow after installing a new program.",
]

def ask(question, temperature=0.2, timeout=600):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": question}],
        "options": {"temperature": temperature},
        "stream": False,
    }
    r = requests.post(URL, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()["message"]["content"]

def main():
    os.makedirs("outputs", exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    temperature = 0.2

    jsonl_path = os.path.join("outputs", "test_outputs.jsonl")
    md_path = os.path.join("outputs", "test_outputs.md")
    csv_path = os.path.join("outputs", "eval_template.csv")

    records = []
    for i, q in enumerate(QUESTIONS, start=1):
        a = ask(q, temperature=temperature)
        rec = {
            "id": i,
            "timestamp": ts,
            "model": MODEL,
            "temperature": temperature,
            "question": q,
            "answer": a,
        }
        records.append(rec)

    # Save JSONL (easy to append and parse)
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Save Markdown (easy to paste into Word)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# IT Helpdesk Chatbot Test Outputs\n\n")
        f.write(f"- Date/Time: {ts}\n- Model: {MODEL}\n- Temperature: {temperature}\n\n")
        for rec in records:
            f.write(f"## Test {rec['id']}\n\n")
            f.write(f"**Question:** {rec['question']}\n\n")
            f.write(f"**Answer:**\n\n{rec['answer']}\n\n---\n\n")

    # Create a scoring template for your analysis section
    headers = [
        "id",
        "issue_topic",
        "clarity_1to5",
        "accuracy_1to5",
        "safety_1to5",
        "completeness_1to5",
        "notes_limitations_hallucinations",
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for rec in records:
            w.writerow([rec["id"], "", "", "", "", "", ""])

    print("Done! Files created:")
    print(" - outputs/test_outputs.jsonl")
    print(" - outputs/test_outputs.md")
    print(" - outputs/eval_template.csv")

if __name__ == "__main__":
    main()
