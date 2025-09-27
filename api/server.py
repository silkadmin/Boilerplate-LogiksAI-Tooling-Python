import os
import json, uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware  # Import CORS Middleware
from dotenv import load_dotenv
import uvicorn
from api.run import run_tool  # Import the dynamic tool execution function
from api.run import list_available_tools
from api.run import list_not_working_tools
from api.run import list_working_tools

load_dotenv()

app = FastAPI()
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all domains
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

def get_cached_result(ref_id):
    file_path = os.path.join(DATA_DIR, f"{ref_id}.json")
    print("file_path" + file_path)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# Background processing task that calls your existing tool
def process_tool_background(tool, message, params, ref_id):
    from tools import unstructured_chunks  # import your tool
    print(f"Started background processing for {ref_id}...")
    params["reference_id"] = ref_id
    unstructured_chunks.run(message, params)  # <- calls your existing run()
    print(f"Finished background processing for {ref_id}")

@app.post("/initiate_run")
async def initiate_run(request: Request, background_tasks: BackgroundTasks):
# async def initiate_run(tool: str, message: str = "", background_tasks: BackgroundTasks = None, **params):
    try:
     
        params = dict(request.query_params)
        tool = params.pop("tool", None)
        message = params.pop("message", "")

        """
        Starts the given tool in the background, returns a reference_id immediately.
        """
        ref_id = str(uuid.uuid4())
        print("initiate_run" + ref_id)
        background_tasks.add_task(process_tool_background, tool, message, params, ref_id)
        print("initiate_run AFTER" + ref_id)
        return {"status": "processing", "reference_id": ref_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error in initiate_run: {e}")


@app.get("/get_result")
async def get_result(reference_id: str):
    print("get_result" + reference_id)
    cached = get_cached_result(reference_id)
    if cached:
        return {"status": "completed", "reference_id": reference_id, "data": cached}
    else:
        return {"status": "processing", "reference_id": reference_id}


@app.post("/run")
async def execute_tool(request: Request):
    try:
        params = dict(request.query_params)
        print(params,flush=True)
        print("params" + str(params),flush=True)
        tool = params.pop("tool", None)
        message = params.pop("message", "")
        # Extract identity if present
        identity = {}
        identity_str = params.pop("identity", "{}")
        try:
            if isinstance(identity_str, str):
                identity = json.loads(identity_str)
            elif isinstance(identity_str, dict):
                identity = identity_str
        except json.JSONDecodeError:
            identity = {}

        # Only add keys if they exist
        if "apikey" in identity:
            params["apikey"] = identity["apikey"]
        if "apisecret" in identity:
            params["apisecret"] = identity["apisecret"]

        if not tool:
            raise HTTPException(status_code=400, detail="Tool parameter is required")

        command = {
            "command": "run",
            "tool": tool,
            "message": message,
            "params": params
        }
        response = run_tool(command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/list_tools")
async def list_tools():
    """
    List all tool names present in the 'tools' folder by returning their filenames without the .py extension.
    """
    tools_dir = "tools"
    tool_names = []

    try:
        response = list_available_tools({"command": "list_tools"})
        return {"tools": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    
@app.get("/unused_list_tools")
async def unused_list_tools():
    """
    List all tool names present in the 'tools' folder by returning their filenames without the .py extension.
    """
    tools_dir = "tools"
    tool_names = []

    try:
        response = list_not_working_tools({"command": "unused_list_tools"})
        return {"tools": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/list_usefull_tools")
async def list_usefull_tools():
    """
    List all tool names present in the 'tools' folder by returning their filenames without the .py extension.
    """
    tools_dir = "tools"
    tool_names = []

    try:
        response = list_working_tools({"command": "list_usefull_tools"})
        return {"tools": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}") 

@app.post("/")
async def health_check():
    return {"status": "running"}

async def run_fastapi_server():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("REST_PORT", 8000))
    config = uvicorn.Config(app, host=host, port=port, loop="asyncio")
    server = uvicorn.Server(config)
    print(f"Rest server started on ws://{host}:{port}")
    await server.serve()
