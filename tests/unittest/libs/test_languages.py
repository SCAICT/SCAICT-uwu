"""
Unit test for scaict_uwu.libs.language.LanguageTagFactory using unittest.
"""

# Future statements
from __future__ import annotations

# Standard imports
import unittest

# Local imports
import scaict_uwu.libs.language


class TestLanguageTagFactory(unittest.TestCase):
    language_tag_factory: scaict_uwu.libs.language.LanguageTagFactory | None

    def setUp(self) -> None:
        self.language_tag_factory = scaict_uwu.libs.language.LanguageTagFactory()

    def tearDown(self) -> None:
        self.language_tag_factory = None

    def test_get(self) -> None:
        language_tag: scaict_uwu.libs.language.LanguageTag = (
            self.language_tag_factory.get_tag(tag="zh-Hant")
        )

        self.assertEqual(language_tag.bcp_47_tag, "zh-Hant")
        self.assertEqual(language_tag.system_message_tag, "zh-hant")
        self.assertEqual(language_tag.discord_code, "zh-TW")

        language_tag = self.language_tag_factory.get_tag(tag="zh-hant")

        self.assertEqual(language_tag.bcp_47_tag, "zh-Hant")
        self.assertEqual(language_tag.system_message_tag, "zh-hant")
        self.assertEqual(language_tag.discord_code, "zh-TW")

    def test_get_by_discord_code(self) -> None:
        language_tag: scaict_uwu.libs.language.LanguageTag | None = (
            self.language_tag_factory.get_by_discord_code(code="zh-TW")
        )

        self.assertIsNotNone(language_tag)
        self.assertEqual(language_tag.bcp_47_tag, "zh-Hant")
        self.assertEqual(language_tag.system_message_tag, "zh-hant")
        self.assertEqual(language_tag.discord_code, "zh-TW")


if __name__ == "__main__":
    unittest.main()
