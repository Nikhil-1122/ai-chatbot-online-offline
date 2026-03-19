from flask import Flask, request, jsonify, render_template, send_from_directory
import requests, os, base64
from PyPDF2 import PdfReader

HF_TOKEN = "your_huggingface_token_here"
HF_MODEL = "anthropic/claude-sonnet-4.5"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

LAST_FILE_TEXT = ""
LAST_FILE_TYPE = ""
LAST_FILE_PATH = ""

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# -------- OFFLINE TEXT (OLLAMA) --------
def offline_ai(prompt, file_text):
    full_prompt = f"""
User uploaded file content:
{file_text}

User question:
{prompt}
"""
    r = requests.post("http://127.0.0.1:11434/api/generate", json={
        "model": "llama3",
        "prompt": full_prompt,
        "stream": False
    })
    return r.json().get("response","No response")

# -------- OFFLINE IMAGE (OLLAMA LLAVA) --------
def offline_image_ai(image_path, prompt):
    try:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")

        r = requests.post("http://127.0.0.1:11434/api/generate", json={
            "model": "llava",
            "prompt": prompt,
            "images": [b64],
            "stream": False
        }, timeout=120)

        data = r.json()
        return data.get("response","No response from image model")

    except Exception as e:
        return "Image error: " + str(e)

# -------- ONLINE (HF) --------
def online_ai(prompt, file_text):
    full_prompt = f"""
User uploaded file content:
{file_text}

User question:
{prompt}
"""
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "model": HF_MODEL,
        "messages": [{"role":"user","content":full_prompt}]
    }
    r = requests.post(url, headers=headers, json=body)
    data = r.json()
    return data["choices"][0]["message"]["content"] if "choices" in data else str(data)

# -------- ROUTES --------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global LAST_FILE_TEXT, LAST_FILE_TYPE, LAST_FILE_PATH
    data = request.json
    msg = data["message"]
    mode = data["mode"]

    if LAST_FILE_TYPE == "image":
        reply = offline_image_ai(LAST_FILE_PATH, msg)
    elif LAST_FILE_TYPE == "text":
        reply = online_ai(msg, LAST_FILE_TEXT) if mode=="online" else offline_ai(msg, LAST_FILE_TEXT)
    else:
        reply = online_ai(msg,"") if mode=="online" else offline_ai(msg,"")

    LAST_FILE_TEXT = ""
    LAST_FILE_TYPE = ""
    LAST_FILE_PATH = ""
    return jsonify({"reply": reply})

@app.route("/upload", methods=["POST"])
def upload():
    global LAST_FILE_TEXT, LAST_FILE_TYPE, LAST_FILE_PATH
    file = request.files["file"]
    path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(path)

    LAST_FILE_TEXT = ""
    LAST_FILE_TYPE = ""
    LAST_FILE_PATH = ""

    name = file.filename.lower()

    if name.endswith(".pdf"):
        reader = PdfReader(path)
        for p in reader.pages:
            LAST_FILE_TEXT += p.extract_text() or ""
        LAST_FILE_TYPE = "text"
        return jsonify({"status":"PDF ready"})

    elif name.endswith(".txt"):
        with open(path,"r",encoding="utf-8") as f:
            LAST_FILE_TEXT = f.read()
        LAST_FILE_TYPE = "text"
        return jsonify({"status":"Text ready"})

    elif name.endswith((".png",".jpg",".jpeg",".webp")):
        LAST_FILE_PATH = path
        LAST_FILE_TYPE = "image"
        return jsonify({
            "status":"Image ready",
            "image_url": f"/uploads/{file.filename}"
        })

    else:
        return jsonify({"status":"Unsupported file"})

if __name__ == "__main__":
    os.makedirs("uploads", exist_ok=True)
    app.run(debug=True)
