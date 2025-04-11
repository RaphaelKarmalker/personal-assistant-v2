from fastapi import FastAPI, WebSocket
from main import HandoffAgentSystem  
import base64
import asyncio

app = FastAPI()
agent = HandoffAgentSystem(debug_time=False)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 Client verbunden")

    try:
        while True:
            data = await websocket.receive_bytes()

            print("🎙️ Audio empfangen. Länge:", len(data), "Bytes")

            audio_bytes = data
            audio_response = await agent.run(audio_bytes)

            if audio_response:
                audio_base64 = base64.b64encode(audio_response).decode("utf-8")
                await websocket.send_text(audio_base64)
                print("🔊 Audio-Antwort gesendet.")
            else:
                await websocket.send_text("[Fehler bei Verarbeitung]")

    except Exception as e:
        print("❌ Fehler im WebSocket:", e)
        await websocket.close()
