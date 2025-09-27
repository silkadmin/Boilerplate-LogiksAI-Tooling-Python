# LogiksAI Tooling - Python

A Python-based tooling server that provides REST API, WebSocket, and LAI Plugin functionality for running tools with background processing capabilities. This server acts as a hot-pluggable tooling interface for the LogiksAI Server ecosystem.

This project serves as a boilerplate for building extensible tooling solutions.

## Features

- **Multi-Protocol Support**: REST API, WebSocket, and LAI Plugin interfaces
- **Dynamic Tool Loading**: Automatically discover and load tools from the tools directory
- **Background Processing**: Asynchronous task execution with reference ID tracking
- **MCP Compatibility**: Compatible with Model Context Protocol standards
- **Hot-Pluggable Architecture**: Add new tools without server restart
- **Cross-Origin Support**: CORS enabled for web applications
- **Environment Configuration**: Flexible configuration via environment variables

## Architecture

The server runs three concurrent services:
- **FastAPI Server**: REST API endpoints (default port: 8000)
- **WebSocket Server**: Real-time communication (default port: 8768)
- **LAI Plugin Server**: Plugin interface for LogiksAI integration

## Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)
- System dependencies for document processing (see installation steps)

## Installation

### 1. Set up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install System Dependencies (Ubuntu/Debian)

For document processing and OCR capabilities:

```bash
sudo apt update && sudo apt install -y \
    tesseract-ocr \
    libtesseract-dev \
    tesseract-ocr-eng \
    tesseract-ocr-jpn \
    tesseract-ocr-chi-sim \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    libmagic-dev \
    poppler-utils \
    python3-dev \
    python3-pip \
    build-essential
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Environment Configuration

Copy the sample environment file and configure:

```bash
cp env_sample .env
```

Edit `.env` with your configuration:
- `HOST`: Server host (default: 0.0.0.0)
- `REST_PORT`: REST API port (default: 8000)
- `SOCKET_PORT`: WebSocket port (default: 8768)
- `LAI_PLUGIN_SERVER`: LAI Plugin server URL
- API keys for various services (Eleven Labs, Serper, Google, etc.)

### 5. Run the Server

```bash
python main.py
```

This starts all three servers concurrently.

## API Endpoints

### REST API

- **POST /run**: Execute a tool synchronously
- **POST /initiate_run**: Start tool execution in background
- **GET /get_result?reference_id={id}**: Get background task result
- **GET /list_tools**: List all available tools
- **GET /list_usefull_tools**: List working tools
- **GET /unused_list_tools**: List non-working tools
- **POST /**: Health check

### WebSocket

Connect to `ws://localhost:8768` and send JSON commands:

```json
{
  "command": "run",
  "tool": "tool_name",
  "message": "input_message",
  "params": {
    "additional": "parameters"
  }
}
```

## Adding New Tools

1. Create a new Python file in the `tools/` directory
2. Implement a `run(message, params)` function
3. The tool will be automatically discovered and available via API

Example tool structure:
```python
def run(message, params):
    # Tool implementation
    return {"result": "tool output"}
```

## Background Processing

For long-running tasks:

1. **Initiate**: POST to `/initiate_run` returns a `reference_id`
2. **Check Status**: GET `/get_result?reference_id={id}` 
3. **Results**: Cached in the `data/` directory as JSON files

## Tool Configuration

Tools are defined in `tools.json` with the following structure:
```json
{
  "toolName": {
    "name": "toolName",
    "description": "Tool description",
    "inputSchema": {
      "type": "object",
      "properties": {
        "param1": {
          "type": "string",
          "description": "Parameter description"
        }
      },
      "required": ["param1"]
    },
    "identitySchema": {
      "type": "object",
      "description": "Identity schema for API",
      "properties": {
        "apikey": {
          "type": "string",
          "description": "API key for authentication"
        }
      },
      "required": ["apikey"]
    }
  }
}
```
