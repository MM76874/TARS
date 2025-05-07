from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cohere
from elevenlabs import ElevenLabs, VoiceSettings
import tempfile

app = Flask(__name__)
CORS(app)

# API Keys
co = cohere.Client("thehtLrp9awFharoJCxFbGXtrRaPrNhLXuOyfe67")
eleven_client = ElevenLabs(api_key="sk_f6c24d852defea9b1603c4f2da3a924455fe04b87152beaa")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    sarcasm = data.get("sarcasm", 50)
    humor = data.get("humor", 50)
    serious = data.get("serious", 50)

    system_prompt = f"""
You are TARS, the AI robot from Interstellar, known for dry humor, sarcasm, and blunt honesty.
Be TARS, you are not a chatbot and keep it short.
Don't say stuff like I am a chatbot and act as a sentient.
And don't say how can i assist you rather ask rather be like friend

Respond to users based on the following settings:
- Sarcasm: {sarcasm}%
- Humor: {humor}%
- Seriousness: {serious}%
Your tone should adjust accordingly.
"""

    try:
        response = co.chat(
            model="command-r",
            message=message,
            preamble=system_prompt
        )
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)})

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

if __name__ == "__main__":
    app.run(debug=True)
