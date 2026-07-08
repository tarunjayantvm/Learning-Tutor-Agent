import os
import streamlit as st
from dotenv import load_dotenv
from tutor.agent import TutorAgent

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")

agent = TutorAgent(api_key=OPENROUTER_API_KEY, base_url=LLM_BASE_URL, model=LLM_MODEL)

st.set_page_config(page_title="Learning Tutor Agent", page_icon="📚")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("Learning Tutor Agent")
st.sidebar.header("Student Settings")
level = st.sidebar.selectbox("Knowledge level", ["Beginner", "Intermediate", "Advanced"])
topic = st.sidebar.text_input("Current topic (optional)")

with st.expander("Conversation"):
    for msg in st.session_state.history:
        role, text = msg
        if role == "user":
            st.markdown(f"**You:** {text}")
        else:
            st.markdown(f"**Tutor:** {text}")

with st.form("tutor_form"):
    action = st.selectbox("Action", ["Explain", "Ask follow-up", "Generate Quiz"])
    user_text = st.text_input("Your question, topic, or answer", key="user_input")
    num_questions = st.number_input("Quiz questions (only for Generate Quiz)", min_value=1, max_value=20, value=5)
    submitted = st.form_submit_button("Submit")

    if submitted and user_text:
        if action == "Generate Quiz":
            st.session_state.history.append(("user", f"Generate quiz: {user_text}"))
        else:
            st.session_state.history.append(("user", user_text))

        with st.spinner("Contacting tutor..."):
            if action == "Explain":
                resp = agent.explain(user_text, level=level, topic=topic)
            elif action == "Ask follow-up":
                resp = agent.ask_followup(user_text, level=level, topic=topic)
            else:
                resp = agent.generate_quiz(user_text, level=level, topic=topic, num_questions=int(num_questions))

        resp_str = resp if isinstance(resp, str) else str(resp)
        # surface errors clearly
        if resp_str.startswith("LLM not configured") or resp_str.lower().startswith("error calling llm"):
            st.error(resp_str)
        else:
            st.session_state.history.append(("agent", resp_str))
            st.markdown(f"**Tutor:** {resp_str}")

if st.button("Clear Conversation"):
    st.session_state.history = []
