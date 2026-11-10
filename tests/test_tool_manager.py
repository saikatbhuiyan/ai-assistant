import unittest
from unittest import mock

from tools.tool_manager import execute_tool, has_word


class TestHasWord(unittest.TestCase):

    def test_matches_a_whole_word(self):
        self.assertTrue(has_word("roll a die", "die"))

    def test_matches_next_to_punctuation(self):
        self.assertTrue(has_word("what time?", "time"))

    def test_ignores_a_word_inside_another_word(self):
        for text in ["keto diet", "he died", "sometimes", "turn clockwise"]:
            with self.subTest(text=text):
                self.assertFalse(has_word(text, "die", "time", "clock"))


# The real tools return random or changing values, so they are replaced
# with fixed ones. These tests only check that the right tool is chosen.
@mock.patch("tools.tool_manager.generate_password", return_value="PASSWORD")
@mock.patch("tools.tool_manager.roll_dice", return_value=4)
@mock.patch("tools.tool_manager.get_current_time", return_value="TIME")
class TestExecuteTool(unittest.TestCase):

    def test_time_questions_use_the_time_tool(self, *_):
        for question in ["What time is it?", "Check the clock", "WHAT TIME IS IT"]:
            with self.subTest(question=question):
                self.assertEqual(execute_tool(question), "TIME")

    def test_dice_requests_use_the_dice_tool(self, *_):
        for question in ["Roll a dice", "Roll a die for me"]:
            with self.subTest(question=question):
                self.assertEqual(execute_tool(question), 4)

    def test_password_requests_use_the_password_tool(self, *_):
        for question in ["Generate a password", "I need new passwords"]:
            with self.subTest(question=question):
                self.assertEqual(execute_tool(question), "PASSWORD")

    def test_password_tool_is_asked_for_12_characters(self, _time, _dice, fake_password):
        execute_tool("Generate a password")

        fake_password.assert_called_once_with(length=12)

    def test_other_questions_go_to_the_model(self, *_):
        for question in ["Explain Python", "Is a keto diet healthy?", "Sometimes I wonder", ""]:
            with self.subTest(question=question):
                self.assertIsNone(execute_tool(question))

    # Known limitation of keyword matching: the word is there, but the user
    # isn't asking for the tool. These pass once tool choice gets smarter.
    @unittest.expectedFailure
    def test_time_complexity_is_not_a_time_request(self, *_):
        self.assertIsNone(execute_tool("Explain time complexity in Python"))

    @unittest.expectedFailure
    def test_password_reset_help_is_not_a_password_request(self, *_):
        self.assertIsNone(execute_tool("How do I reset my Gmail password?"))


if __name__ == "__main__":
    unittest.main()
