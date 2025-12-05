import asyncio
import websockets
import base64

# Path to the local audio file
AUDIO_PATH = "test_audio.wav"
OUTPUT_PATH = "reply.mp3"

# Server URI (e.g., localhost or actual IP address)
SERVER_URI = "ws://localhost:8000/ws"

async def send_audio():
    # Read the audio file as bytes
    with open(AUDIO_PATH, "rb") as audio_file:
        audio_bytes = audio_file.read()

    async with websockets.connect(SERVER_URI) as websocket:
        print("🎙️ Sending audio to server...")
        await websocket.send(audio_bytes)

        # Wait for the server's response (Base64 encoded MP3)
        response = await websocket.recv()
        print("🔊 Response received!")

        # Decode and save the response
        try:
            audio_data = base64.b64decode(response)
            with open(OUTPUT_PATH, "wb") as out_file:
                out_file.write(audio_data)
            print(f"✅ Response saved as: {OUTPUT_PATH}")
        except Exception as e:
            print("❌ Error decoding the response:", e)

if __name__ == "__main__":
    asyncio.run(send_audio())
