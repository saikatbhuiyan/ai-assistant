import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Create AI client
client = OpenAI(base_url=os.getenv("BASE_URL"), api_key=os.getenv("API_KEY"))


def build_tool_descriptions(tools) -> str:
    """
    Turn the tools reported by an MCP server into text the planner can read.

    Args:
        tools (list): Tools from discover_tools(), each with a name and a description.

    Returns:
        str: One "Tool: ... / Description: ..." block per tool.
    """
    descriptions = ""

    for tool in tools:
        descriptions += f"""
Tool: {tool.name}
Description: {tool.description or "No description."}
"""

    return descriptions


def choose_tool(user_request: str, tools) -> str:
    """
    Choose the appropriate tool based on the user's request.

    Args:
        user_request (str): The user's request.
        tools (list): The tools the MCP server offers, from discover_tools().

    Returns:
        str: The name of the chosen tool, or "none" if no tool is appropriate.
    """
    prompt = f"""
You are an AI planner. Based on the user's request, select the most
appropriate tool from the available tools.

Available tools:
{build_tool_descriptions(tools)}

Instructions:
If no tool is appropriate, reply with: none
Otherwise, reply only with the name of the tool that best fits the request.
Do not explain.

User request:
{user_request}
"""
    response = client.chat.completions.create(

        model=os.getenv("MODEL"),

        messages=[
            {
                "role":"system",
                "content":"You are an AI planner."
            },
            {
                "role":"user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    # The model may answer "None" or add spaces and newlines around the name
    return content.strip().lower() if content else "none"
