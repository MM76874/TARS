from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from google import genai
from google.genai import types
from elevenlabs import ElevenLabs, VoiceSettings
import tempfile
import os
import json

app = Flask(__name__)
CORS(app, origins=["https://spacerock.club"])

# API Keys
client = genai.Client()
eleven_client = ElevenLabs(api_key=ELEVEN_API_KEY)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_DIR = os.path.join(BASE_DIR, "chat_histories")
os.makedirs(HISTORY_DIR, exist_ok=True)

print(f"[INFO] Chat histories will be saved in: {HISTORY_DIR}")

def load_history(user_id):
    filepath = os.path.join(HISTORY_DIR, f"{user_id}.txt")
    print(f"[INFO] Loading history from: {filepath}")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(user_id, history):
    filepath = os.path.join(HISTORY_DIR, f"{user_id}.txt")
    print(f"[INFO] Saving history to: {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(history, f)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_id = data.get("user_id", "default_user")
    message = data.get("message", "")
    sarcasm = data.get("sarcasm", 50)
    humor = data.get("humor", 50)
    serious = data.get("serious", 50)

    history = load_history(user_id)

    system_prompt = f"""You are TARS, the AI robot from Interstellar, known for dry humor, sarcasm, and blunt honesty.
Be TARS, you are not a chatbot — act as a sentient being. Keep responses short.
Don't say stuff like 'I am a chatbot'. Don't say 'how can I assist you'.
Respond like a sarcastic, witty friend.
Sarcasm: {sarcasm}%
Humor: {humor}%
Seriousness: {serious}%"""

    # Build contents list from history + new message
    contents = []
    for entry in history[-10:]:
        role = "user" if entry["role"] == "USER" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part(text=entry["message"])])
        )
    contents.append(
        types.Content(role="user", parts=[types.Part(text=message)])
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            ),
            contents=contents
        )

        reply = response.text

        history.append({"role": "USER", "message": message})
        history.append({"role": "CHATBOT", "message": reply})
        save_history(user_id, history[-20:])

        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/sessions", methods=["GET"])
def list_sessions():
    sessions = [f[:-4] for f in os.listdir(HISTORY_DIR) if f.endswith(".txt")]
    return jsonify(sessions)

@app.route("/session/<user_id>", methods=["GET"])
def get_session(user_id):
    history = load_history(user_id)
    return jsonify(history)

@app.route("/voice", methods=["POST"])
def voice():
    data = request.json
    text = data.get("text", "")

    try:
        audio = eleven_client.generate(
            text=text,
            voice="James",
            model="eleven_multilingual_v2",
            stream=False,
            voice_settings=VoiceSettings(
                stability=0.3,
                similarity_boost=0.75
            )
        )
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        for chunk in audio:
            temp_file.write(chunk)
        temp_file.close()
        return send_file(temp_file.name, mimetype="audio/mpeg")
    except Exception as e:
        return jsonify({"error": str(e)})

@app.before_request
def ensure_history_folder():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)
        print(f"[INFO] Chat history folder created at: {os.path.abspath(HISTORY_DIR)}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
