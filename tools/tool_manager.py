import re

from tools.tools import generate_password, get_current_time, roll_dice


def has_word(text, *words):
    """Return True if any of the words appears in text as a whole word."""

    return any(re.search(rf"\b{word}\b", text) for word in words)


def match_keyword(user_input):
    """Pick a tool name from keywords in the text, or None if none match."""

    text = user_input.lower()

    if has_word(text, "time", "clock"):
        return "get_current_time"

    if has_word(text, "dice", "die"):
        return "roll_dice"

    if has_word(text, "password", "passwords"):
        return "generate_password"

    return None


def execute_tool(user_input, tool_name=None):
    """
    Run a tool and return its result, or None if no tool should run.

    When tool_name is given (for example by the planner), only that tool can
    run, and unknown names such as "none" run nothing. Without a tool_name,
    the tool is picked by keywords in user_input.
    """

    if tool_name is None:
        tool_name = match_keyword(user_input)

    if tool_name == "get_current_time":
        return get_current_time()

    if tool_name == "roll_dice":
        return roll_dice()

    if tool_name == "generate_password":
        return generate_password(length=12)

    return None
