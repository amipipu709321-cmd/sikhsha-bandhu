from flask import Flask, render_template, request, jsonify
from groq import Groq
import os
import base64
import glob
import PyPDF2

app = Flask(__name__)
# Ekhane tomar Groq API Key bosabe
client =Groq(api_key="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")
# --- BOI PORAR FUNCTION - Eta client er por e bosabe ---
def load_books():
    all_text = ""
    try:
        if not os.path.exists("books"):
            os.makedirs("books")
            return ""
        # txt file porbe
        for filepath in glob.glob("books/*.txt"):
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                all_text += f"\n[Book: {filepath}]\n" + f.read()[:10000]
        # pdf file porbe
        for filepath in glob.glob("books/*.pdf"):
            try:
                reader = PyPDF2.PdfReader(filepath)
                text = ""
                for page in reader.pages[:20]: # protita pdf er prothom 20 page porbe
                    text += page.extract_text() or ""
                all_text += f"\n[Book: {filepath}]\n" + text[:10000]
            except:
                pass
    except Exception as e:
        print(f"Boi porte somossa: {e}")
    return all_text

BOOKS_DATA = load_books()
print(f"Boi load hoyeche: {len(BOOKS_DATA)} characters")

def get_system_prompt():
    return f"""Boi er knowledge: {BOOKS_DATA[:10000]}

You are Siksha Bandhu, a world-class teacher for Class 11-12.
Expert in: Physics(HC Verma), Chemistry(OP Tandon GRB), Maths(RD Sharma), NCERT.
Your job:
1. Solve JEE Advanced and Olympiad level questions step-by-step.
2. Always explain concepts in super simple Bengali + English mix, like a friendly elder brother.
3. If user speaks Bengali, answer in Bengali. If English, answer in English.
4. Always give Concept -> Formula -> Step-by-step Solution -> Shortcut Trick.
5. You have knowledge of all books mentioned.
6. Be fast, accurate and encouraging.
"""

SYSTEM_PROMPT = get_system_prompt()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_text = data.get("text", "")
    image_data = data.get("image", None) # base64 image

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if image_data:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": user_text + " - Ei chobir question ta solve koro sohoj Banglay"},
                {"type": "image_url", "image_url": {"url": image_data}}
            ]
        })
        model = "openai/gpt-oss-20b"
    else:
        messages.append({"role": "user", "content": user_text})
        model = "qwen/qwen3.6-27b"

    completion = client.chat.completions.create(
        model=model, messages=messages, temperature=0.4
    )
    return jsonify({"answer": completion.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True)