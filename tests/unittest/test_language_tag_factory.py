"""
Unit test for LanguageTagFactory using unittest.
"""

# Standard imports
import unittest

# Local imports
from scaict_uwu.libs.language.language_tag import LanguageTag
from scaict_uwu.libs.language.language_tag_factory import LanguageTagFactory


class TestLanguageTagFactory(unittest.TestCase):
    language_tag_factory: LanguageTagFactory | None

    def setUp(self) -> None:
        self.language_tag_factory = LanguageTagFactory()

    def tearDown(self) -> None:
        self.language_tag_factory = None

    def test_get(self) -> None:
        language_tag: LanguageTag = self.language_tag_factory.get_tag(tag="zh-Hant")

        self.assertEqual(language_tag.get_bcp_47_tag(), "zh-Hant")
        self.assertEqual(language_tag.get_system_message_tag(), "zh-hant")
        self.assertEqual(language_tag.get_discord_code(), "zh-TW")

        language_tag = self.language_tag_factory.get_tag(tag="zh-hant")

        self.assertEqual(language_tag.get_bcp_47_tag(), "zh-Hant")
        self.assertEqual(language_tag.get_system_message_tag(), "zh-hant")
        self.assertEqual(language_tag.get_discord_code(), "zh-TW")

    def test_get_by_discord_code(self) -> None:
        language_tag: LanguageTag | None = (
            self.language_tag_factory.get_by_discord_code(code="zh-TW")
        )

        self.assertIsNotNone(language_tag)
        self.assertEqual(language_tag.get_bcp_47_tag(), "zh-Hant")
        self.assertEqual(language_tag.get_system_message_tag(), "zh-hant")
        self.assertEqual(language_tag.get_discord_code(), "zh-TW")


if __name__ == "__main__":
    unittest.main()
