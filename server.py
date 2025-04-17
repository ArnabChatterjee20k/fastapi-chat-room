from fastapi import FastAPI, WebSocket, WebSocketDisconnect
app = FastAPI()

@app.get("/")
def home():
    return {"target":"HOmmmmmmeeeee"}

connected_clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            for client in connected_clients:
                await client.send_text(f"Message: {data}")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)