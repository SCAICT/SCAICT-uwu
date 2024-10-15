"""
This is the module for the class for all system messages.
"""

# Local imports
from ..language.language import Language


class Message:
    """
    The Message class deals with fetching and processing of system messages.
    """

    __use_lang: str | None = None
    """
    __use_lang (str|None): The language tag of the language for the system\
        message to use.
    """

    __in_lang: str | None = None
    """
    __in_lang (str|None): The language tag of the language that the system\
        message actually used.
    """

    def __init__(
        self,
        key: str,
        params: list,
        use_lang: Language | None,
    ) -> None:
        """
        Set the language tag of the language that the message expected to use.

        Parameters:
            key (str): Message key.
            params (list): Message parameters.
            use_lang: (Language|None): Language to use (None: defaults to\
                current user language).
        """

    def set_lang(self, lang_tag: str) -> None:
        """
        Set the language tag of the language that the message expected to use.

        Parameters:
            lang_tag (str): The language tag of the language that the message\
                expected to use.
        """

        self.__use_lang = lang_tag

    def get_lang(self) -> str:
        """
        Get the final language tag of the language that the message used or\
            falls back to.

        Returns:
            str: Description of return value.
        """

        return self.__use_lang or self.__in_lang or ""
