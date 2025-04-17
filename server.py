from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import json

app = FastAPI()

connected_clients = set()

@app.get("/")
async def get():
    html = """
    <html>
        <head><title>Event WebSocket</title></head>
        <body>
            <h2>WebSocket Event Test</h2>
            <textarea id="log" rows="10" cols="40" readonly></textarea><br/>
            <input id="msg" type="text" placeholder="Type a message" />
            <button onclick="sendMessage()">Send</button>

            <script>
                const ws = new WebSocket("ws://localhost:8000/ws");

                ws.onmessage = (event) => {
                    const log = document.getElementById("log");
                    log.value += event.data + "\\n";
                };

                function sendMessage() {
                    const input = document.getElementById("msg");
                    const payload = {
                        event: "add_message",
                        data: input.value
                    };
                    ws.send(JSON.stringify(payload));
                    input.value = "";
                }
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
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
                    # Broadcast to all clients
                    for client in connected_clients:
                        await client.send_text(response)
                else:
                    await websocket.send_text("[Error] Unknown event")
            except json.JSONDecodeError:
                await websocket.send_text("[Error] Invalid JSON format")
    except WebSocketDisconnect:
        connected_clients.remove(websocket)