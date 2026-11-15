from pathlib import Path

from fastmcp import Client

# Found next to this file, so it works from any folder
SERVER_PATH = Path(__file__).parent / "server.py"


async def connect():
    """
    Starts the MCP server and connects to it.

    Returns:
        Client: The connected client, to pass to the other functions.
    """

    client = Client(SERVER_PATH)
    await client.__aenter__()

    return client


async def disconnect(client):
    """
    Disconnects from the MCP server, which also stops it.
    """

    await client.__aexit__(None, None, None)


async def discover_tools(client):
    """
    Asks the MCP server which tools it offers.

    Returns:
        list: The tools, each with a name and a description.
    """

    return await client.list_tools()


async def execute_tool(client, tool_name, arguments=None):
    """
    Runs a tool on the MCP server.

    Args:
        client (Client): The connected client.
        tool_name (str): The name of the tool to run.
        arguments (dict): The tool's arguments, for example {"length": 16}.

    Returns:
        The tool's result, for example 4 for roll_dice.
    """

    result = await client.call_tool(tool_name, arguments or {})

    return result.data
