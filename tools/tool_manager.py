import re

from tools.tools import generate_password, get_current_time, roll_dice


def has_word(text, *words):
    """Return True if any of the words appears in text as a whole word."""

    return any(re.search(rf"\b{word}\b", text) for word in words)


def execute_tool(user_input, tool_name=None):

    text = user_input.lower()

    if tool_name == "get_current_time" or has_word(text, "time", "clock"):
        return get_current_time()

    if tool_name == "roll_dice" or has_word(text, "dice", "die"):
        return roll_dice()

    if tool_name == "generate_password" or has_word(text, "password", "passwords"):
        return generate_password(length=12)

    return None
