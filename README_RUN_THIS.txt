IT Helpdesk Chatbot (Ollama) — Assignment Pack

1) Install Ollama (one-time)
   - Windows/macOS/Linux: https://ollama.com

2) Start Ollama server (Terminal #1)
   ollama serve

3) Pull a base model (Terminal #2)
   ollama pull llama3:8b

4) Create your helpdesk model
   ollama create helpdesk -f Helpdesk.Modelfile

5) Quick sanity test
   ollama run helpdesk

6) Run the Streamlit web UI
   pip install -r requirements.txt
   streamlit run app.py

7) Generate test outputs (for your report)
   python run_tests.py

Files saved under outputs/:
   - test_outputs.md (paste into your report)
   - test_outputs.jsonl
   - eval_template.csv (fill your scores & notes)
