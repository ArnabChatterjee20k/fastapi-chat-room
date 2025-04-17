from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
from db import add_message,get_all_messages

app = FastAPI()

connected_clients = set()
messages = [] # in memory cache

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    # 👇 Send previous messages ONLY to the newly joined client
    for msg in get_all_messages():
        await websocket.send_text(f"[Previous] {msg.message}")
    try:
        while True:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
                event = payload.get("event")
                data = payload.get("data")
                # Handle different events
                if event == "add_message":
                    response = f"[New Message] {data}"
                    messages.append(data)
                    add_message(data)
                    # Broadcast to all clients
                    for client in connected_clients:
                        await client.send_text(response)
                else:
                    await websocket.send_text("[Error] Unknown event")
            except json.JSONDecodeError:
                await websocket.send_text("[Error] Invalid JSON format")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)