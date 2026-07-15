# 🎓 Learning Tutor Agent

An AI-powered **Learning Tutor Agent** built with **Streamlit** and an **OpenRouter-compatible LLM**. The application adapts explanations to the student's knowledge level, asks intelligent follow-up questions to assess understanding, generates quizzes and practice problems, and provides personalized feedback with study recommendations through an interactive chat interface.

---

## ✨ Features

- 📚 Personalized concept explanations
- 🧠 Adapts responses based on the student's knowledge level
- ❓ Intelligent follow-up questions to assess understanding
- 📝 AI-generated quizzes and practice problems
- 📊 Personalized feedback and study recommendations
- 💬 Interactive tutoring conversation
- ⚡ Powered by OpenRouter-compatible Large Language Models
- 🎨 Clean and responsive Streamlit interface

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **OpenRouter API**
- **Large Language Models (LLMs)**
- **python-dotenv**

---

## 📂 Project Structure

```text
.
├── app.py
├── tutor/
│   └── agent.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/learning-tutor-agent.git
cd learning-tutor-agent
```

Create and activate a virtual environment.

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root.

```env
OPENROUTER_API_KEY=your_openrouter_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1/chat/completions
LLM_MODEL=your_model_name
```

---

## ▶️ Run the Application

```bash
streamlit run app.py
```

The application will automatically open in your default browser.

---

---

## 🎯 How It Works

1. Select your **knowledge level** (Beginner, Intermediate, or Advanced).
2. Optionally specify the **current topic**.
3. Ask a question or request an explanation.
4. The AI explains concepts based on your level.
5. Generate quizzes or ask follow-up questions to test your understanding.
6. Receive personalized feedback and study recommendations.

---

## 🌟 Future Enhancements

- 🎙️ Voice-based tutoring
- 📈 Learning progress tracking
- 🏆 Gamified quizzes and achievements
- 📄 Downloadable study notes
- 📚 Flashcard generation
- 🌐 Multi-language support
- 📱 Mobile-responsive interface

---

Deployed Link: https://learning-tutor-agent-9hr74syhszhmate4gmwqvf.streamlit.app/

⭐ If you found this project useful, consider giving it a **Star** on GitHub!
