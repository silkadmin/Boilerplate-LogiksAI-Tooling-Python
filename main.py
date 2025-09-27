import asyncio
import sys
import os


project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


print("Python executable:", sys.executable)
print("sys.path:", sys.path)

from api.server import run_fastapi_server
from api.socket import start_websocket_server
from api.laiplugin import start_laiplugin_server

async def run_servers():
    fastapi_task = asyncio.create_task(run_fastapi_server())
    websocket_task = asyncio.create_task(start_websocket_server())
    laiplugin_task = asyncio.create_task(start_laiplugin_server())
    await asyncio.gather(fastapi_task, websocket_task, laiplugin_task)

if __name__ == "__main__":
    asyncio.run(run_servers())
