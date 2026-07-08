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
            "You are a helpful, patient tutoring assistant. Provide clear explanations and examples, "
            "adapted to the student's knowledge level. Keep explanations concise and actionable."
        )
        user = f"Level: {level}\n"
        if topic:
            user += f"Topic: {topic}\n"
        user += f"Explain the following concept or question:\n{prompt}\nInclude an example and a brief checklist to verify understanding."

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
        return self._call(messages)

    def ask_followup(self, prompt, level="Beginner", topic=""):
        system = "You are a tutor that asks one focused follow-up question to assess student understanding."
        user = f"Student said: {prompt}\nProvide one clear follow-up question to assess comprehension, and suggest what a correct answer should include."
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        return self._call(messages)

    def generate_quiz(self, prompt, level="Beginner", topic="", num_questions: int = 5):
        system = "You are a tutor generating short quizzes with answers and brief explanations."
        user = (
            f"Create a quiz of {num_questions} questions for a {level} student."
            f" Topic: {topic}\nFocus: {prompt}\nReturn numbered questions followed by answers and brief explanations."
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
