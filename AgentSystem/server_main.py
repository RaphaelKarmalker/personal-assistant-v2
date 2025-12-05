from fastapi import FastAPI, WebSocket
from main import HandoffAgentSystem  
import base64
import asyncio

app = FastAPI()
agent = HandoffAgentSystem(debug_time=False)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Accept the WebSocket connection
    await websocket.accept()
    print("🔌 Client connected")

    try:
        while True:
            # Receive audio data from the client
            data = await websocket.receive_bytes()

            print("🎙️ Audio received. Length:", len(data), "Bytes")

            audio_bytes = data
            audio_response = await agent.run(audio_bytes)

            if audio_response:
                # Encode the audio response to Base64 and send it back
                audio_base64 = base64.b64encode(audio_response).decode("utf-8")
                await websocket.send_text(audio_base64)
                print("🔊 Audio response sent.")
            else:
                # Send an error message if processing fails
                await websocket.send_text("[Error during processing]")

    except Exception as e:
        # Handle WebSocket errors
        print("❌ WebSocket error:", e)
        await websocket.close()
