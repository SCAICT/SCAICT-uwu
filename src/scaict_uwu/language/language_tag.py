"""
This is the module for the class for all languages.
"""


class LanguageTag:
    """
    The LanguageTag class deals with language data.
    """

    _tag: str
    """
    _tag (str): The BCP 47 language subtag of the LanguageTag object.
    """

    def __init__(self, language_tag) -> None:
        pass

    def get_bcp_47_tag(self) -> str | None:
        pass

    def get_discord_code(self) -> str | None:
        pass

    def get_fallbacks(self) -> list | None:
        pass
