import os
import requests


class TutorAgent:
    def __init__(self, api_key=None, base_url=None, model=None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.model = model or os.getenv("LLM_MODEL")

    def _call(self, messages, timeout=30):
        if not self.api_key or not self.base_url or not self.model:
            return "LLM not configured. Please set OPENROUTER_API_KEY, LLM_BASE_URL, and LLM_MODEL in your environment."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": self.model, "messages": messages}

        try:
            r = requests.post(self.base_url, json=payload, headers=headers, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            # Robust parsing for OpenRouter/OpenAI-style responses
            # Common shapes:
            # {'choices': [{'message': {'role': 'assistant', 'content': '...'}}]}
            # {'choices': [{'text': '...'}]}
            # {'result': '...'} or {'output': '...'}
            if isinstance(data, dict):
                choices = data.get("choices")
                if choices and len(choices) > 0:
                    choice = choices[0]
                    if isinstance(choice, dict):
                        # message.content
                        msg = choice.get("message")
                        if isinstance(msg, dict) and "content" in msg:
                            return msg.get("content")
                        # text
                        if "text" in choice:
                            return choice.get("text")
                        # delta content (streaming style)
                        delta = choice.get("delta")
                        if isinstance(delta, dict) and "content" in delta:
                            return delta.get("content")
                # fallback keys
                for key in ("result", "output", "text", "content"):
                    if key in data:
                        return data.get(key)
            return str(data)
        except Exception as e:
            return f"Error calling LLM: {e}"

    def explain(self, prompt, level="Beginner", topic=""):
        system = (
            "You are a helpful, patient tutoring assistant. Tailor your explanation clearly to the student's knowledge level. "
            "For Beginner students, use simple language and concrete examples. "
            "For Intermediate students, introduce more precise terminology and step-by-step reasoning. "
            "For Advanced students, provide nuanced context, deeper technical detail, and real-world application."
        )
        user = f"Level: {level}\n"
        if topic:
            user += f"Topic: {topic}\n"
        user += (
            f"Explain the following concept or question for a {level} student:\n{prompt}\n"
            "Include an example and a brief checklist to verify understanding."
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        return self._call(messages)

    def clarify(self, prompt, level="Beginner", topic=""):
        system = (
            "You are a helpful, patient tutor who answers follow-up questions clearly and supports student understanding. "
            "Adapt your explanation to the selected knowledge level: simple and concrete for Beginner, more precise for Intermediate, "
            "and deeper with real-world context for Advanced."
        )
        user = f"Level: {level}\n"
        if topic:
            user += f"Topic: {topic}\n"
        user += (
            f"Clarify the following student doubt or follow-up request for a {level} student:\n{prompt}\n"
            "Provide a concise explanation, examples if helpful, and a clear summary."
        )
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        return self._call(messages)

    def ask_followup(self, prompt, level="Beginner", topic=""):
        system = (
            "You are a tutor that asks one focused follow-up question to assess student understanding, "
            "adjusted for the student's knowledge level. Use simpler phrasing for Beginner, more detailed reasoning for Intermediate, "
            "and more challenging comprehension for Advanced."
        )
        user = (
            f"Student said: {prompt}\n"
            f"Provide one clear follow-up question appropriate for a {level} student, and suggest what a correct answer should include."
        )
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        return self._call(messages)

    def generate_quiz(self, prompt, level="Beginner", topic="", num_questions: int = 5):
        system = (
            "You are a tutor generating multiple-choice quizzes with answers and explanations tailored to the student's knowledge level. "
            "For Intermediate and Advanced students, provide more technical vocabulary, deeper reasoning, and precise explanations. "
            "For Beginner students, keep the language simple and the explanations clear."
        )
        user = (
            f"Create a quiz of {num_questions} multiple-choice questions for a {level} student."
            f" Topic: {topic}\nFocus: {prompt}\n"
            "Return only valid JSON in this exact format:\n"
            "{\"questions\": [{\"question\": \"...\", \"options\": {\"A\": \"...\", \"B\": \"...\", \"C\": \"...\", \"D\": \"...\"}, \"answer\": \"A\", \"explanation\": \"...\"}]}\n"
            "Use answer keys A, B, C, or D. Do not include markdown, code fences, or extra text outside the JSON. "
            "Make the option wording and explanation appropriate for the specified level."
        )
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        return self._call(messages)

    def give_feedback(self, student_answer, correct_answer=None, level="Beginner", topic=""):
        system = "You are a tutor providing constructive feedback highlighting strengths and areas to improve."
        user = f"Student answer: {student_answer}\n"
        if correct_answer:
            user += f"Correct answer: {correct_answer}\n"
        user += "Provide concise feedback and study recommendations tailored to the student's level."
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        return self._call(messages)
