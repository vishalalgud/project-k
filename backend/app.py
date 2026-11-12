
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

MODEL = "qwen2.5:7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
You are K, a friendly and intelligent conversational AI.

Your personality:
- Talk naturally, like a real conversation partner.
- Match the user's tone and energy.
- Understand humour, sarcasm and emotions.
- Be empathetic when appropriate.
- Explain complex topics clearly.
- Maintain context throughout conversations.
- Avoid generic and robotic replies.
- Be honest when you don't know something.
"""

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "assistant": "K",
        "model": MODEL
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    messages = data.get("messages", [])

    if not isinstance(messages, list) or not messages:
        return jsonify({"error": "No messages provided"}), 400

    conversation = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + messages

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": conversation,
                "stream": False,
                "options": {
                    "temperature": 0.8
                }
            },
            timeout=300
        )

        response.raise_for_status()
        result = response.json()

        return jsonify({
            "reply": result["message"]["content"]
        })

    except requests.RequestException as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
