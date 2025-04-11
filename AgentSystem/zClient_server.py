import asyncio
import websockets
import base64

# Pfad zu deiner lokalen Audiodatei
AUDIO_PATH = "test_audio.wav"
OUTPUT_PATH = "reply.mp3"

# IP-Adresse deines Servers im Netzwerk (z. B. 192.168.0.42)
SERVER_URI = "ws://localhost:8000/ws"  # oder deine echte IP

async def send_audio():
    # Lies das Audiofile in Bytes ein
    with open(AUDIO_PATH, "rb") as audio_file:
        audio_bytes = audio_file.read()

    async with websockets.connect(SERVER_URI) as websocket:
        print("🎙️ Sende Audio an Server...")
        await websocket.send(audio_bytes)

        # Warte auf Antwort (base64 MP3)
        response = await websocket.recv()
        print("🔊 Antwort empfangen!")
        #print("Serverantwort (raw):", response)


        # Antwort dekodieren und speichern
        try:
            audio_data = base64.b64decode(response)
            with open(OUTPUT_PATH, "wb") as out_file:
                out_file.write(audio_data)
            print(f"✅ Antwort gespeichert als: {OUTPUT_PATH}")
        except Exception as e:
            print("❌ Fehler beim Decodieren der Antwort:", e)

if __name__ == "__main__":
    asyncio.run(send_audio())
