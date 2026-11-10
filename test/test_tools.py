import string
import unittest
from datetime import datetime
from unittest import mock

from tools.tools import generate_password, get_current_time, roll_dice


class TestGetCurrentTime(unittest.TestCase):

    def test_formats_day_month_year_and_12_hour_time(self):
        # Month (11) and minutes (05) differ, so mixing up %m and %M fails this test
        fixed_now = datetime(2026, 11, 9, 14, 5, 9)

        with mock.patch("tools.tools.datetime") as fake_datetime:
            fake_datetime.now.return_value = fixed_now
            self.assertEqual(get_current_time(), "09-11-2026 02:05:09 PM")

    def test_returns_the_real_current_time(self):
        result = datetime.strptime(get_current_time(), "%d-%m-%Y %I:%M:%S %p")

        self.assertLess(abs((datetime.now() - result).total_seconds()), 5)


class TestRollDice(unittest.TestCase):

    def test_rolls_are_between_1_and_6(self):
        for _ in range(1000):
            self.assertIn(roll_dice(), range(1, 7))

    def test_every_face_comes_up(self):
        rolls = {roll_dice() for _ in range(1000)}

        self.assertEqual(rolls, {1, 2, 3, 4, 5, 6})


class TestGeneratePassword(unittest.TestCase):

    def test_default_length_is_12(self):
        self.assertEqual(len(generate_password()), 12)

    def test_custom_length(self):
        self.assertEqual(len(generate_password(length=20)), 20)

    def test_uses_only_letters_digits_and_punctuation(self):
        allowed = set(string.ascii_letters + string.digits + string.punctuation)

        self.assertTrue(set(generate_password(length=200)) <= allowed)

    def test_passwords_are_different_each_time(self):
        passwords = {generate_password() for _ in range(100)}

        self.assertEqual(len(passwords), 100)


if __name__ == "__main__":
    unittest.main()
