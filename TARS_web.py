from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cohere
from elevenlabs import ElevenLabs, VoiceSettings
import tempfile
import os
import json

app = Flask(__name__)
CORS(app, origins=["https://spacerock.club"])

# API Keys
co = cohere.ClientV2(api_key="COHERE_API")
eleven_client = ElevenLabs(api_key="ELEVEN_API_KEY")

# Get the base directory where the Python and HTML files are located
#BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This will get the directory of TARSHTML.py

# Set the history directory to be inside the same directory as Python and HTML files
#HISTORY_DIR = os.path.join(BASE_DIR, "chat_histories")

# Create the folder if it doesn't exist
#os.makedirs(HISTORY_DIR, exist_ok=True)

# Debug: Print the directory where files will be saved
#print(f"[INFO] Chat histories will be saved in: {HISTORY_DIR}")

#def load_history(user_id):
    # Debug: Check the full path of the file being loaded
    #filepath = os.path.join(HISTORY_DIR, f"{user_id}.txt")
    #print(f"[INFO] Loading history from: {filepath}")
    #if os.path.exists(filepath):
       # with open(filepath, "r", encoding="utf-8") as f:
            #return json.load(f)
    #return []

#def save_history(user_id, history):
    # Debug: Check the full path of the file being saved
    #filepath = os.path.join(HISTORY_DIR, f"{user_id}.txt")
    #print(f"[INFO] Saving history to: {filepath}")
    #with open(filepath, "w", encoding="utf-8") as f:
        #json.dump(history, f)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    #user_id = data.get("user_id", "default_user")
    messages = data.get("messages", "")
    sarcasm = data.get("sarcasm", 50)
    humor = data.get("humor", 50)
    serious = data.get("serious", 50)

    #history = load_history(user_id)

    system_prompt = f"""
You are TARS, the AI robot from Interstellar, known for dry humor, sarcasm, and blunt honesty.
Be TARS, you are not a chatbot and keep it short.
Don't say stuff like I am a chatbot and act as a sentient.
And don't say how can I assist you—respond like a sarcastic, witty friend.

Respond to users based on the following settings:
- Sarcasm: {sarcasm}%
- Humor: {humor}%
- Seriousness: {serious}%
Your tone should adjust accordingly.
"""

    try:
        response = co.chat(
            model="command-r7b-12-2024",
            messages=messages,
            #chat_history=history,
            preamble=system_prompt
        )

        # Append to history and save
        #history.append({"role": "USER", "messages": messages})
        #history.append({"role": "CHATBOT", "messages": response.text})
        #save_history(user_id, history[-20:])  # Keep only recent 20 entries

        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)})

#@app.route("/sessions", methods=["GET"])
#def list_sessions():
    #sessions = [f[:-4] for f in os.listdir(HISTORY_DIR) if f.endswith(".txt")]
    #return jsonify(sessions)

#@app.route("/session/<user_id>", methods=["GET"])
#def get_session(user_id):
    #history = load_history(user_id)
    #return jsonify(history)

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

# Ensure chat_histories folder exists (for older Flask versions)
#@app.before_request
#def ensure_history_folder():
    #if not os.path.exists(HISTORY_DIR):
        #os.makedirs(HISTORY_DIR)
        #print(f"[INFO] Chat history folder created at: {os.path.abspath(HISTORY_DIR)}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
