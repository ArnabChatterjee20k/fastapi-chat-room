from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
import json
from db import add_message, get_all_messages
import asyncio
from contextlib import asynccontextmanager

connected_clients = set()
messages = []  # in-memory cache
import time 
async def clear_messages():
    global messages
    while True:
        messages = [] 
        await asyncio.sleep(600)

@asynccontextmanager
async def startup_event(app: FastAPI):
    asyncio.create_task(clear_messages())
    yield

app = FastAPI(lifespan=startup_event)


@app.get("/")
def serve():
    return FileResponse("index.html")

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
