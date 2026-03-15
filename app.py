from flask import Flask, render_template, request, jsonify
import json
import os
import google.generativeai as genai

app = Flask(__name__)

# Gemini API configuration
genai.configure(api_key="AIzaSyBAla6IMZEGyKWFaCagV0R5Qlc0n9T6lag")

model = genai.GenerativeModel("gemini-2.5-flash")

# Education keywords for domain restriction
education_keywords = [
    "study","education","teacher","student","school","college",
    "university","exam","subject","math","science","physics",
    "chemistry","biology","history","geography","english",
    "computer","programming","python","java","coding",
    "assignment","homework","lesson","course"
]


# Check if question belongs to education domain
def is_education_question(question):

    question = question.lower()

    for word in education_keywords:
        if word in question:
            return True

    return False


# Save chat history to JSON
def save_chat(user_message, bot_reply):

    file_path = "chat_history.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            history = json.load(f)
    else:
        history = []

    history.append({
        "user": user_message,
        "bot": bot_reply
    })

    with open(file_path, "w") as f:
        json.dump(history, f, indent=4)


# Load history API
@app.route("/history")
def history():

    file_path = "chat_history.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    return jsonify(data)


# Homepage
@app.route("/")
def home():
    return render_template("index.html")


# Chat API
@app.route("/chat", methods=["POST"])
def chat():

    data = request.json
    user_message = data.get("message", "")

    # Domain restriction
    if not is_education_question(user_message):

        bot_reply = "⚠️ This chatbot only answers education related questions."

        save_chat(user_message, bot_reply)

        return jsonify({"reply": bot_reply})

    try:

        response = model.generate_content(user_message)

        bot_reply = response.text

        save_chat(user_message, bot_reply)

        return jsonify({"reply": bot_reply})

    except Exception as e:

        return jsonify({
            "reply": "Error generating response",
            "error": str(e)
        })


# Run server
if __name__ == "__main__":
    app.run(debug=True)