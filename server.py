from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json
from db import add_message, get_all_messages

app = FastAPI()

connected_clients = set()
messages = []  # in-memory cache

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)

    try:
        if messages:
            for msg in messages:
                await websocket.send_text(f"[Previous] {msg}")
        else:
            db_messages = get_all_messages()
            for msg in db_messages:
                messages.append(msg.message)
                await websocket.send_text(f"[Previous] {msg.message}")

        while True:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
                event = payload.get("event")
                data = payload.get("data")

                if event == "add_message":
                    response = f"[New Message] {data}"
                    messages.append(data)  # cache it
                    add_message(data)      # save to DB
                    # Broadcast to all clients
                    for client in connected_clients:
                        await client.send_text(response)
                else:
                    await websocket.send_text("[Error] Unknown event")

            except json.JSONDecodeError:
                await websocket.send_text("[Error] Invalid JSON format")

    except WebSocketDisconnect:
        connected_clients.remove(websocket)
