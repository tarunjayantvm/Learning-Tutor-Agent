# Learning Tutor Agent

Streamlit app that acts as a tutoring assistant: explains concepts, asks follow-ups, generates quizzes, and provides feedback.

Getting started

1. Create a Python environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and set your `OPENROUTER_API_KEY`.

3. Run the app:

```bash
streamlit run app.py
```

Files added

- [app.py](app.py) — Streamlit UI
- [tutor/agent.py](tutor/agent.py) — LLM client and tutor logic
- [.env.example](.env.example) and [.env](.env) — environment variables (do not commit `.env`)
- [requirements.txt](requirements.txt) — dependencies

Notes

- The app calls an OpenRouter-compatible chat completions endpoint. Ensure your `LLM_BASE_URL` and `LLM_MODEL` are correct for your provider.
