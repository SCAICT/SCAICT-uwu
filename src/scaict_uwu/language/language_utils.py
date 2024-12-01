"""
This is the module for the class for language utilities.
"""


class LanguageUtils:
    """
    The LanguageUtils class deals with language utilities.
    """

    @staticmethod
    def get_supported_discord_codes() -> list:
        """
        Get the Discord locale codes supported by Discord.

        See Pycord discord.commands.core valid_locales (not public)
        See <https://discord.com/developers/docs/reference#locales>

        Returns:
            list: The list of Discord locale codes supported by Discord.
        """

        return [
            "bg",
            "cs",
            "da",
            "de",
            "el",
            "en-GB",
            "en-US",
            # 'es-419' was missing from Pycord
            "es-419",
            "es-ES",
            "fi",
            "fr",
            "hi",
            "hr",
            "hu",
            # 'id' was missing from Pycord
            "id",
            "it",
            "ja",
            "ko",
            "lt",
            "nl",
            "no",
            "pl",
            "pt-BR",
            "ro",
            "ru",
            "sv-SE",
            "th",
            "tr",
            "uk",
            "vi",
            "zh-CN",
            "zh-TW",
        ]

    @staticmethod
    def get_discord_code_mapping() -> dict:
        """
        Get the mapping of BCP 47 language tag to Discord locale code.

        Returns:
            dict: The mapping of BCP 47 language tag to Discord locale code.
        """

        return {
            "en": "en-US",
            "es": "es-ES",
            "nb": "no",
            "sv": "sv-SE",
            "zh-Hans": "zh-CN",
            "zh-Hant": "zh-TW",
        }

    @classmethod
    def get_discord_code_to_bcp_47_mapping(cls) -> dict:
        """
        Get the mapping of Discord locale code to BCP 47 language tag.

        Returns:
            dict: The mapping of Discord locale code to BCP 47 language tag.
        """

        return {v: k for k, v in cls.get_discord_code_mapping()}

    @classmethod
    def get_discord_code(cls, code) -> str:
        """
        Get the BCP 47 language tag from Discord locale code.

        Returns:
            str: the mapping of Discord locale code to BCP 47 language tag.
        """

        return cls.get_discord_code_mapping().get(code, code)

    @classmethod
    def get_bcp_47_from_discord_code(cls, code) -> str:
        """
        Get the BCP 47 language tag from Discord locale code.

        Returns:
            str: the mapping of Discord locale code to BCP 47 language tag.
        """

        return cls.get_discord_code_to_bcp_47_mapping().get(code, code)
