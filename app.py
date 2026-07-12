import os
import json
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
if "last_quiz" not in st.session_state:
    st.session_state.last_quiz = []
if "quiz_results" not in st.session_state:
    st.session_state.quiz_results = []

def parse_quiz_response(response):
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end != -1 and start < end:
            try:
                data = json.loads(response[start:end+1])
            except json.JSONDecodeError:
                return None
        else:
            return None
    if not isinstance(data, dict):
        return None
    questions = data.get("questions")
    if not isinstance(questions, list):
        return None
    parsed_questions = []
    for item in questions:
        if not isinstance(item, dict):
            return None
        question = item.get("question")
        options = item.get("options")
        answer = item.get("answer")
        explanation = item.get("explanation", "")
        if not question or not options or not answer:
            return None
        if isinstance(options, list):
            mapped = {}
            for idx, opt in enumerate(options):
                if idx >= 4:
                    break
                mapped[chr(ord("A") + idx)] = str(opt).strip()
            options = mapped
        if not isinstance(options, dict):
            return None
        normalized_options = {k.strip().upper(): str(v).strip() for k, v in options.items()}
        normalized_answer = str(answer).strip().upper()
        if normalized_answer not in normalized_options:
            for key, value in normalized_options.items():
                if normalized_answer == value.strip().upper():
                    normalized_answer = key
                    break
        parsed_questions.append({
            "question": str(question).strip(),
            "options": normalized_options,
            "answer": normalized_answer,
            "explanation": str(explanation).strip(),
        })
    return parsed_questions

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
    action = st.selectbox("Action", ["Explain", "Clarify doubt", "Generate Quiz"])
    user_text = st.text_area("Your question, topic, or answer", key="user_input", height=120)
    followup_text = ""
    if action == "Clarify doubt":
        followup_text = st.text_area(
            "Follow-up question or clarification request",
            key="followup_input",
            height=120,
            help="Ask a follow-up question to clarify your doubt or build on the previous prompt.",
        )
    num_questions = st.number_input("Quiz questions (only for Generate Quiz)", min_value=1, max_value=20, value=5)
    submitted = st.form_submit_button("Submit")

    if submitted:
        prompt_text = user_text.strip()
        if action == "Clarify doubt":
            prompt_text = followup_text.strip() or prompt_text

        if prompt_text:
            if action == "Generate Quiz":
                st.session_state.history.append(("user", f"Generate quiz: {prompt_text}"))
            else:
                st.session_state.history.append(("user", prompt_text))

            with st.spinner("Contacting tutor..."):
                if action == "Explain":
                    resp = agent.explain(prompt_text, level=level, topic=topic)
                elif action == "Clarify doubt":
                    resp = agent.clarify(prompt_text, level=level, topic=topic)
                else:
                    resp = agent.generate_quiz(prompt_text, level=level, topic=topic, num_questions=int(num_questions))

            resp_str = resp if isinstance(resp, str) else str(resp)
            # surface errors clearly
            if resp_str.startswith("LLM not configured") or resp_str.lower().startswith("error calling llm"):
                st.error(resp_str)
            else:
                if action == "Generate Quiz":
                    parsed_quiz = parse_quiz_response(resp_str)
                    if parsed_quiz:
                        st.session_state.last_quiz = parsed_quiz
                        st.session_state.quiz_results = []
                        st.session_state.history.append(("agent", f"Generated a {len(parsed_quiz)}-question quiz for {level} level."))
                        st.success("Quiz generated successfully. Select your answers below.")
                    else:
                        st.session_state.last_quiz = []
                        st.session_state.history.append(("agent", resp_str))
                        st.error("Could not parse the quiz into an interactive format. Showing raw quiz output below.")
                        st.markdown(f"**Tutor:** {resp_str}")
                else:
                    st.session_state.history.append(("agent", resp_str))
                    st.markdown(f"**Tutor:** {resp_str}")
        else:
            st.error("Please enter your main prompt or follow-up question before submitting.")

if st.session_state.last_quiz:
    with st.form("quiz_answer_form"):
        st.markdown("## Answer the Quiz")
        unanswered = False
        for idx, quiz_item in enumerate(st.session_state.last_quiz):
            st.markdown(f"**{idx + 1}. {quiz_item['question']}**")
            options = quiz_item["options"]
            answer_key = f"quiz_answer_{idx}"
            choice = st.selectbox(
                "",
                options=["Select an answer"] + list(options.keys()),
                format_func=lambda key, options=options: "Select an answer" if key == "Select an answer" else f"{key}. {options[key]}",
                key=answer_key,
                index=0,
            )
            if choice == "Select an answer":
                unanswered = True
        submitted_answers = st.form_submit_button("Submit Answers")

        if submitted_answers:
            if unanswered:
                st.error("Please select an answer for every question before submitting.")
            else:
                results = []
                for idx, quiz_item in enumerate(st.session_state.last_quiz):
                    selected = st.session_state.get(f"quiz_answer_{idx}", "Select an answer")
                    correct = quiz_item["answer"].strip().upper()
                    selected_text = quiz_item["options"].get(selected, "")
                    correct_text = quiz_item["options"].get(correct, "")
                    if selected == correct:
                        result = f"**Question {idx + 1}: Correct**\n\n"
                    else:
                        result = f"**Question {idx + 1}: Wrong**\n\n"
                    result += f"Your answer: {selected}. {selected_text}\n\n"
                    result += f"Correct answer: {correct}. {correct_text}\n\n"
                    result += f"Explanation: {quiz_item.get('explanation', '')}"
                    results.append(result)
                st.session_state.quiz_results = results

    if st.session_state.quiz_results:
        st.markdown("## Quiz Results")
        for result in st.session_state.quiz_results:
            st.markdown(result)

if st.button("Clear Conversation"):
    st.session_state.history = []
    st.session_state.last_quiz = []
    st.session_state.quiz_results = []
