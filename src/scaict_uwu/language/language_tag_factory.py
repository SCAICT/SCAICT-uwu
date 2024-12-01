"""
This is the module for creating the objects for all languages.
"""

# Local imports
from .language_tag import LanguageTag
from .language_utils import LanguageUtils


class LanguageTagFactory:
    """
    The LanguageTagFactory class deals with LanguageTag object creations.
    """

    _tags: dict[str, LanguageTag] = {}
    """
    _tags (dict): The LanguageTag objects.
    """

    def __init__(self) -> None:
        pass

    def get_tag(self, tag) -> LanguageTag:
        """
        Get LanguageTag object by BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the responding BCP 47\
                language tag.
        """

        if not tag in self._tags:
            self._tags[tag] = LanguageTag(tag)

        return self._tags[tag]

    def get_tag_by_discord_code(self, code) -> LanguageTag | None:
        """
        Get LanguageTag object by BCP 47 language tag.

        Returns:
            (LanguageTag | None): The LanguageTag object to the responding\
                Discord locale code. Return None when is not a supported\
                Discord locale code.
        """

        if not code in LanguageUtils.get_supported_discord_codes():
            return None

        tag = LanguageUtils.get_bcp_47_from_discord_code(code)

        if not tag in self._tags:
            self._tags[tag] = LanguageTag(tag)

        return self._tags[tag]
