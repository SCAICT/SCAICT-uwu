"""
This is the module for creating the objects for all languages.
"""

# Local imports
from .language_tag import LanguageTag


class LanguageTagFactory:
    """
    The LanguageTagFactory class deals with LanguageTag object creations.
    """

    _tags: dict = {}
    """
    _tags (dict): The LanguageTag objects.
    """

    def __init__(self) -> None:
        pass

    def get_tag(self) -> LanguageTag | None:
        pass

    def get_tag_by_discord_code(self) -> LanguageTag | None:
        pass
