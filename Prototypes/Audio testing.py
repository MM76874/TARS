from elevenlabs import ElevenLabs

# Initialize the client with your API key
client = ElevenLabs(api_key="sk_067850dde3fcc8de4309fc3303e8d71508d1921a1bf165e9")

# Use the generate method with text
response = client.generate(
    text="Hello, this is a test message from Eleven Labs using the generate method."
)

# Assuming response is a generator, let's write it to a file
with open('output_audio.wav', 'wb') as audio_file:
    for chunk in response:
        audio_file.write(chunk)
