from api.common.agent_runner import run_tool_agent

def run(message: str, payload: dict):
    return run_tool_agent(message, payload, tool_scope=["airtable"])
