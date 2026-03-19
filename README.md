# 🤖 AI Chatbot (Online + Offline + File-Aware)

A full-stack AI chatbot that works both **online and offline**, supports **PDF, text, and image uploads**, and allows users to ask questions about uploaded content in real-time.

---

## 🚀 Features

- 🌐 Online + Offline AI (Auto switching based on internet)
- 📄 PDF, Text & Image understanding
- 🖼️ Image preview inside chat
- 🎤 Voice input support
- 📊 Markdown + LaTeX (Math) rendering
- 🌙 Modern dark UI chat interface
- ⚡ Real-time responses with loading indicator
- 🔒 Temporary file context (no permanent storage)

---

## 🧠 Tech Stack

**Frontend**
- HTML, CSS, JavaScript

**Backend**
- Flask (Python)

**AI Models**
- Offline: Ollama (LLaMA3, LLaVA)
- Online: Hugging Face API

**Libraries**
- requests
- PyPDF2

---

## ⚙️ Setup Instructions

### 1. Clone Repository
git clone https://github.com/your-username/ai-chatbot.git
cd ai-chatbot

### 2. Install Dependencies
pip install -r requirements.txt

### 3. Install Ollama (Offline AI)

Download from: https://ollama.com

Run the text model:
ollama run llama3
For image understanding (vision model):
ollama run llava

### 4. Add Hugging Face API Key
Open app.py and replace:
HF_TOKEN = "your_huggingface_token_here"

### 5. Run the Application
python app.py
Open in browser:
http://127.0.0.1:5000
