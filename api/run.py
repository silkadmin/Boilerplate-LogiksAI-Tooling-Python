import importlib
import importlib.util
from pathlib import Path
import os
import json

def list_available_tools(command_data):
    """
    List all tool names present in the 'tools' folder by returning their filenames without the .py extension.

    Args:
        command_data (dict): JSON structure with 'command'.

    Returns:
        dict: JSON response with tool names if the command is 'list_tools'.
    """
    tools_dir = "tools"  # Folder where all tool modules are stored
    config_path = os.path.join(os.path.dirname(tools_dir), "tools.json")
    tool_names = []

    try:
        # Debugging output
        #print(f"Command received: {command_data.get('command')}")
        # print(f"Listing Tools")

        tools_config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                tools_config = json.load(f)
        else:
            print(f"Warning: Config file '{config_path}' not found. Using default tool metadata.")
        # print(tools_config)
        
        # Validate command type
        # if command_data.get("command") != "list_tools":
        #     return {"error": "Invalid command."}

        # Check if tools directory exists
        if not os.path.exists(tools_dir):
            raise FileNotFoundError(f"Directory '{tools_dir}' not found.")

        # print(f"Tools Directory Path: {os.path.abspath(tools_dir)}")
        # print(f"Files in Directory: {os.listdir(tools_dir)}")

        # Iterate through all files in the directory
        # List all .py files excluding __init__.py or hidden files
        for file in os.listdir(tools_dir):
            if file.endswith(".py") and not file.startswith("__") and not file.startswith("z_"):  # Ignore __init__.py and hidden files
                tool_name = file[:-3]  # Remove the '.py' extension
                if tool_name in tools_config:
                    tool_names.append(tools_config[tool_name])
                else:
                    tool_names.append({"name": tool_name, "description": f"Tool used for - {tool_name}",  "inputSchema": {} })

        return  tool_names

    except Exception as e:
        return {"error": f"Error accessing tools directory: {e}"}         


def list_working_tools(command_data):
    """
    List all tool names present in the 'tools' folder but only include tools with meaningful data
    from 'tools.json' (i.e., tools that have non-empty inputSchema or identitySchema).

    Args:
        command_data (dict): JSON structure with 'command'.

    Returns:
        list: List of tool metadata dictionaries for tools that have data.
    """
    tools_dir = "tools"  # Folder where all tool modules are stored
    config_path = os.path.join(os.path.dirname(tools_dir), "tools.json")
    # config_path = os.path.join(tools_dir, "tools.json")
    tool_names = []

    try:
        print("Listing Available Tools with meaningful data...")

        # Load metadata from tools.json
        tools_config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                tools_config = json.load(f)
        else:
            print(f"Warning: Config file '{config_path}' not found. Using default metadata.")

        # Ensure tools folder exists
        if not os.path.exists(tools_dir):
            raise FileNotFoundError(f"Directory '{tools_dir}' not found.")

        # Iterate all .py files in tools_dir
        for file in os.listdir(tools_dir):
            if file.endswith(".py") and not file.startswith("__"):
                tool_name = file[:-3]  # remove .py extension

                if tool_name in tools_config:
                    tool_data = tools_config[tool_name]

                    # Only include if inputSchema or identitySchema is non-empty
                    has_input = "inputSchema" in tool_data and tool_data["inputSchema"]
                    has_identity = "identitySchema" in tool_data and tool_data["identitySchema"]

                    if has_input or has_identity:
                        tool_names.append(tool_data)
                    else:
                        # Skip tools that have empty schemas
                        continue

        return tool_names

    except Exception as e:
        return {"error": f"Error accessing tools directory: {e}"}




def list_not_working_tools(command_data):
    """
    List all tool names from 'tools' folder but only include tools with meaningful data
    from 'unused_tools.json' (i.e., tools that have non-empty inputSchema or identitySchema).

    Args:
        command_data (dict): JSON structure with 'command'.

    Returns:
        list: List of tool metadata dictionaries for tools that have data.
    """
    tools_dir = "tools"  # Folder where all tool modules are stored
    config_path = os.path.join(os.path.dirname(tools_dir), "unused_tools.json")
    tool_names = []

    try:
        print("Listing Unused Tools with meaningful data...")

        # Load metadata from unused_tools.json
        tools_config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                tools_config = json.load(f)
        else:
            print(f"Warning: Config file '{config_path}' not found. Using default metadata.")

        # Ensure tools folder exists
        if not os.path.exists(tools_dir):
            raise FileNotFoundError(f"Directory '{tools_dir}' not found.")

        # Iterate all .py files in tools_dir
        for file in os.listdir(tools_dir):
            if file.endswith(".py") and not file.startswith("__"):
                tool_name = file[:-3]  # remove .py extension

                if tool_name in tools_config:
                    tool_data = tools_config[tool_name]

                    # Only include if inputSchema or identitySchema is non-empty
                    has_input = "inputSchema" in tool_data and tool_data["inputSchema"]
                    has_identity = "identitySchema" in tool_data and tool_data["identitySchema"]

                    if has_input or has_identity:
                        tool_names.append(tool_data)
                    else:
                        # Skip tools that have empty schemas
                        continue

        return tool_names

    except Exception as e:
        return {"error": f"Error accessing tools directory: {e}"}


def run_tool(command):
    """
    Dynamically run the specified tool or list available tools.

    Args:
        command (dict): JSON command containing the tool name, message, and parameters.

    Returns:
        dict: Response from the executed tool or error details.
    """
    print(command)
    tool_name = command.get("tool", "").strip().lower()
    # data = command.get("data", {})
    message = command.get("message", "")
    params = command.get("params", {})


    # Handle 'list_tools' command directly
    if command.get("command") == "list_tools":
        return list_available_tools(command)
    if command.get("command")== "unused_list_tools":
        return list_unused_tools(command)
    if command.get("command") == "list_usefull_tools":
        return list_usefull_tools(command)
 
    try:
        # First, attempt a normal package import (tools.<name>)
        module_name = f"tools.{tool_name}"
        print(module_name)
        try:
            tool_module = importlib.import_module(module_name)
        except ModuleNotFoundError:
            # Fallback: import by absolute file path to be resilient to CWD/PYTHONPATH issues
            tools_dir = Path(__file__).resolve().parent.parent / "tools"
            tool_path = tools_dir / f"{tool_name}.py"
            if not tool_path.exists():
                return {"status": "error", "message": f"Tool '{tool_name}' not found in the 'tools' folder."}
            spec = importlib.util.spec_from_file_location(module_name, str(tool_path))
            if spec is None or spec.loader is None:
                return {"status": "error", "message": f"Unable to load tool '{tool_name}' from {tool_path}."}
            tool_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tool_module)

        if hasattr(tool_module, "run"):
            response = tool_module.run(message, params)
            return {"response": response}
        else:
            return {"status": "error", "message": f"The tool '{tool_name}' does not have a 'run' method."}

    except ModuleNotFoundError:
        return {"status": "error", "message": f"Tool '{tool_name}' not found in the 'tools' folder."}
    except Exception as e:
        return {"status": "error", "message": f"An error occurred while running the tool: {e}"}








# def list_available_tools():
#     """
#     List all tool names present in the 'tools' folder by returning their filenames without the .py extension.

#     Returns:
#         list: A list of tool names (filenames without the .py extension).
#     """
#     tools_dir = "tools"  # Folder where all tool modules are stored
#     tool_names = []

#     try:
#         # Check if tools directory exists
#         if not os.path.exists(tools_dir):
#             raise FileNotFoundError(f"Directory '{tools_dir}' not found.")

#         # Iterate through all files in the directory
#         for file in os.listdir(tools_dir):
#             if file.endswith(".py") and not file.startswith("__"):  # Ignore __init__.py and hidden files
#                 tool_name = file[:-3]  # Remove the '.py' extension
#                 tool_names.append(tool_name)

#     except Exception as e:
#         print(f"Error accessing tools directory: {e}")

#     return tool_names

# _______________________

# def run_tool(command):
#     """
#     Dynamically run the specified tool by importing its module and calling the `run` method with multiple arguments.

#     Args:
#         command (dict): JSON command containing the tool name, message, and parameters.

#     Returns:
#         dict: Response from the executed tool or error details.
#     """
#     tool_name = command.get("tool", "").lower()  # Get the tool name and convert to lowercase
#     data = command.get("data", {})
#     message = data.get("message", "")  # Get the message (query)
#     params = data.get("params", {})  # Get the params (arguments like URL)

#     try:
#         # Dynamically import the tool module (e.g., tools.smart_scraper)
#         module_name = f"tools.{tool_name}"
#         tool_module = importlib.import_module(module_name)

#         # Check if the module has a `run` method
#         if hasattr(tool_module, "run"):
#             # Call the `run()` method with the message and params
#             response = tool_module.run(message, params)  # Pass both message and params
#             return {"status": "success", "response": response}
#         else:
#             return {"status": "error", "message": f"The tool '{tool_name}' does not have a 'run' method."}

#     except ModuleNotFoundError:
#         return {"status": "error", "message": f"Tool '{tool_name}' not found in the 'tools' folder."}
#     except Exception as e:
#         return {"status": "error", "message": f"An error occurred while running the tool: {e}"}
