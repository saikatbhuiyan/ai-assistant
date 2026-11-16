import os
import unittest
from types import SimpleNamespace
from unittest import mock

# planner.py creates an OpenAI client on import, which needs some API key
os.environ.setdefault("API_KEY", "test")

from planner import build_tool_descriptions, choose_tool


def make_tool(name, description):
    """A stand-in for a tool from discover_tools(): only name and description are used."""

    return SimpleNamespace(name=name, description=description)


TOOLS = [
    make_tool("get_current_time", "Returns the current date and time."),
    make_tool("get_weather", "Returns the weather for a city."),
]


def fake_reply(content):
    """A stand-in for client.chat.completions.create() that always replies with content."""

    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )
    return mock.patch("planner.client.chat.completions.create", return_value=response)


class TestBuildToolDescriptions(unittest.TestCase):

    def test_lists_every_tool_with_its_description(self):
        text = build_tool_descriptions(TOOLS)

        self.assertIn("Tool: get_current_time\nDescription: Returns the current date and time.", text)
        self.assertIn("Tool: get_weather\nDescription: Returns the weather for a city.", text)

    def test_tool_without_description(self):
        text = build_tool_descriptions([make_tool("roll_dice", None)])

        self.assertIn("Description: No description.", text)
        self.assertNotIn("None", text)

    def test_no_tools_gives_empty_text(self):
        self.assertEqual(build_tool_descriptions([]), "")


class TestChooseTool(unittest.TestCase):

    def test_prompt_lists_the_discovered_tools(self):
        with fake_reply("get_weather") as create:
            choose_tool("Is it raining?", TOOLS)

        prompt = create.call_args.kwargs["messages"][-1]["content"]

        self.assertIn("get_weather", prompt)
        self.assertIn("Is it raining?", prompt)

    def test_prompt_has_no_hard_coded_tools(self):
        with fake_reply("none") as create:
            choose_tool("Hello", [make_tool("get_weather", "Weather.")])

        prompt = create.call_args.kwargs["messages"][-1]["content"]

        for name in ["roll_dice", "generate_password", "get_current_time"]:
            with self.subTest(name=name):
                self.assertNotIn(name, prompt)

    def test_reply_is_cleaned(self):
        for reply, expected in [
            (" get_weather\n", "get_weather"),
            ("None", "none"),
            ("GET_CURRENT_TIME", "get_current_time"),
        ]:
            with self.subTest(reply=reply), fake_reply(reply):
                self.assertEqual(choose_tool("anything", TOOLS), expected)

    def test_empty_reply_means_no_tool(self):
        with fake_reply(None):
            self.assertEqual(choose_tool("anything", TOOLS), "none")


if __name__ == "__main__":
    unittest.main()
