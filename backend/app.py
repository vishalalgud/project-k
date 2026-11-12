
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from database import (
    initialize_database,
    create_conversation,
    conversation_exists,
    save_message,
    get_messages
)

app = Flask(__name__)
CORS(app)

MODEL = "qwen2.5:7b"
OLLAMA_URL = "http://localhost:11434/api/chat"

SYSTEM_PROMPT = """
You are K, a friendly and intelligent conversational AI.

Personality:
- Talk naturally and expressively.
- Match the user's tone and energy.
- Understand humour and sarcasm.
- Be empathetic when appropriate.
- Give meaningful and accurate explanations.
- Maintain conversational context.
- Avoid robotic and repetitive answers.
- Be honest when you don't know something.
"""

initialize_database()


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

    message = data.get("message", "")
    conversation_id = data.get("conversation_id")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message cannot be empty"}), 400

    if conversation_id is None:
        conversation_id = create_conversation()

    elif not isinstance(conversation_id, str) or not conversation_exists(conversation_id):
        return jsonify({"error": "Invalid conversation ID"}), 404

    message = message.strip()

    # Save user message
    save_message(conversation_id, "user", message)

    # Retrieve conversation history
    history = get_messages(conversation_id)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + history

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": 0.8
                }
            },
            timeout=300
        )

        response.raise_for_status()

        result = response.json()
        reply = result["message"]["content"]

        # Save assistant response
        save_message(conversation_id, "assistant", reply)

        return jsonify({
            "assistant": "K",
            "conversation_id": conversation_id,
            "reply": reply
        })

    except requests.RequestException as error:
        return jsonify({"error": str(error)}), 500


@app.route("/conversations/<conversation_id>", methods=["GET"])
def conversation_history(conversation_id):

    if not conversation_exists(conversation_id):
        return jsonify({"error": "Conversation not found"}), 404

    return jsonify({
        "conversation_id": conversation_id,
        "messages": get_messages(conversation_id)
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
