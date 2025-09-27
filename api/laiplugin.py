import os
import json
import websockets
import asyncio
from dotenv import load_dotenv
from api.run import run_tool

RECONNECT_INTERVAL = 15

async def start_laiplugin_server():
    uri = os.getenv("LAI_PLUGIN_SERVER", "ws://localhost:8000/tools")
    token = os.getenv("LAI_PLUGIN_AUTH", "")
    headers = [
        ("Authorization", f"Bearer {token}")
    ]
    #, extra_headers=headers

    while True:
	    try:
	        async with websockets.connect(uri) as websocket:
	            print("Connected to LAI Plugin Socket server")
	            
	            while True:
	                try:
	                    # Wait for incoming command
	                    command_data = await websocket.recv()
	                    command = json.loads(command_data)
	                    print(f"Received WebSocket command: {command}")

	                    # Process command
	                    if 'command' in command:
	                        msgid = command["msgid"]
	                        result = run_tool(command)
	                        response = {
	                            "status": "success",
	                            "msgid": msgid,
	                            "data": result
	                        }
	                    elif 'type' in command:
	                        response = {
	                            "status": "success",
	                            "ack": "true"
	                        }
	                    else:
	                        response = {
	                            "status": "error",
	                            "message": "No command field in received instructions"
	                        }
	                    
	                    print(f"Sending - {response}")

	                    # Send response
	                    await websocket.send(json.dumps(response))

	                except websockets.exceptions.ConnectionClosed:
	                    print("Connection closed by server.")
	                    break
	                except json.JSONDecodeError:
	                    print("Received invalid JSON.")
	                except Exception as e:
	                    print(f"Processing error: {e}")
	                    await websocket.send(json.dumps({
	                        "status": "error",
	                        "message": str(e)
	                    }))

	    except Exception as e:
	        print(f"Connection failed: {e}")
	    
	    print(f"Retrying LAI Plugin Server Connection in {RECONNECT_INTERVAL} seconds...")
	    await asyncio.sleep(RECONNECT_INTERVAL)
