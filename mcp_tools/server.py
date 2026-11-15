import random
import secrets
import string
from datetime import datetime

from fastmcp import FastMCP

mcp = FastMCP("This is a test MCP server.")


@mcp.tool("get_current_time")
def get_current_time() -> str:
    """
    Returns the current date and time as a string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@mcp.tool("roll_dice")
def roll_dice(sides: int = 6) -> int:
    """
    Rolls a dice with the specified number of sides and returns the result.
    """
    return random.randint(1, sides)


@mcp.tool("generate_password")
def generate_password(length: int = 12) -> str:
    """
    Generates a secure random password of the specified length.
    """
    # secrets, not random: random is predictable and unsafe for passwords
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


if __name__ == "__main__":
    # The assistant starts this server itself, and the server's output would
    # appear in the chat, so the banner and info logs are turned off.
    # Never print() here: stdout carries the MCP messages.
    mcp.run(show_banner=False, log_level="WARNING")
