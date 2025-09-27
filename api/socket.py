import os
import json
import websockets
from dotenv import load_dotenv
from api.run import run_tool

load_dotenv()

async def start_websocket_server():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("SOCKET_PORT", 8768))

    async def websocket_handler(websocket):
        try:
            while True:
                command_data = await websocket.recv()
                command = json.loads(command_data)
                print(f"Received WebSocket command: {command}")

                response = run_tool(command)
                await websocket.send(json.dumps(response))
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")
        except Exception as e:
            print(f"WebSocket Error: {e}")
            await websocket.send(json.dumps({"status": "error", "message": "An error occurred"}))

    server = await websockets.serve(websocket_handler, host, port)
    print(f"WebSocket server started on ws://{host}:{port}")
    await server.wait_closed()
