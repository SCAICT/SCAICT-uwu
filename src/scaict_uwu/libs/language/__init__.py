"""
This is the module for languages.
"""

# Future statements
from __future__ import annotations

# Standard imports
import functools
import typing


class LanguageTag:
    """
    The LanguageTag class deals with language data.

    Note:
        This class is designed to be instantiated through LanguageTagFactory\
        rather than directly.

        Example:
            language_tag_factory = LanguageTagFactory()
            tag = language_tag_factory.get("zh-Hant")
            tag = language_tag_factory.get_by_discord_code("zh-TW")
    """

    def __init__(self, *, tag: str) -> None:
        """
        Parameters:
            tag (str): BCP 47 language tag.
        """

        self._tag: str = tag
        """
        The BCP 47 language subtag of the LanguageTag object.
        """

    @functools.cached_property
    def bcp_47_tag(self) -> str:
        """
        Get the BCP 47 language tag of the LanguageTag object.

        Returns:
            str: The BCP 47 language tag.
        """

        return self._tag

    @functools.cached_property
    def system_message_tag(self) -> str:
        """
        Get the system message language tag of the LanguageTag object.

        Returns:
            str: The system message language tag.
        """

        return self._tag.lower()

    @functools.cached_property
    def discord_code(self) -> str | None:
        """
        Get the Discord locale code of the LanguageTag object.

        See <https://discord.com/developers/docs/reference#locales>

        Returns:
            (str | None): The Discord locale code. Return None when there is no\
                corresponding supported Discord locale code.
        """

        return LanguageUtils.get_discord_code(tag=self._tag)

    @functools.cached_property
    def fallbacks(self) -> list[str]:
        """
        Get the language fallback chain of the LanguageTag object.

        Returns:
            list[str]: The list containing BCP 47 language tags of the language\
                fallback chain.
        """

        return []


class LanguageTagFactory:
    """
    The LanguageTagFactory class deals with LanguageTag object creations.
    """

    _tags: typing.ClassVar[dict[str, LanguageTag]] = {}
    """
    _tags (dict): The LanguageTag objects.
    """

    def _get_tag_internal(self, *, tag: str) -> LanguageTag:
        """
        Get LanguageTag object by normalized BCP 47 language tag.

        Parameters:
            tag (str): Normalized BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the corresponding BCP 47\
                language tag.
        """

        if tag not in self._tags:
            self._tags[tag] = LanguageTag(tag=tag)

        return self._tags[tag]

    def get_tag(self, *, tag: str) -> LanguageTag:
        """
        Get LanguageTag object by normalized BCP 47 language tag.

        Parameters:
            tag (str): Normalized BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the corresponding BCP 47\
                language tag.
        """

        tag = LanguageUtils.to_bcp_47_case(tag=tag)

        return self._get_tag_internal(tag=tag)

    def get_by_unnormalized(self, *, tag: str) -> LanguageTag:
        """
        Get LanguageTag object by unnormalized BCP 47 language tag.

        Parameters:
            tag (str): Unnormalized BCP 47 language tag.

        Returns:
            LanguageTag: The LanguageTag object to the corresponding BCP 47\
                language tag.
        """

        tag = LanguageUtils.to_bcp_47(tag=tag)

        return self._get_tag_internal(tag=tag)

    def get_by_discord_code(self, *, code: str) -> LanguageTag | None:
        """
        Get LanguageTag object by Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            (LanguageTag | None): The LanguageTag object of the corresponding\
                Discord locale code. Return None when is not a supported\
                Discord locale code.
        """

        if code not in LanguageUtils.get_supported_discord_codes():
            return None

        tag = LanguageUtils.get_from_discord_code(code=code)

        return self._get_tag_internal(tag=tag)


class LanguageUtils:
    """
    The LanguageUtils class deals with language utilities.
    """

    @staticmethod
    def get_bcp_47_prefix_mapping() -> dict[str, str]:
        """
        Get the mapping of unnormalized BCP 47 language tag prefix to\
        normalized BCP 47 language tag prefix.

        Returns:
            dict[str, str]: The mapping of unnormalized BCP 47 language tag\
                prefix to normalized BCP 47 language tag prefix.
        """

        return {
            "art-lojban": "jbo",
            "en-GB-oed": "en-GB-oxendict",
            "i-ami": "ami",
            "i-bnn": "bnn",
            "i-hak": "hak",
            "i-klingon": "tlh",
            "i-lux": "lb",
            "i-navajo": "nv",
            "i-pwn": "pwn",
            "i-tao": "tao",
            "i-tay": "tay",
            "i-tsu": "tsu",
            "no-bok": "nb",
            "no-nyn": "nn",
            "sgn-BE-FR": "sfb",
            "sgn-BE-NL": "vgt",
            "sgn-BR": "bzs",
            "sgn-CH-DE": "sgg",
            "sgn-CO": "csn",
            "sgn-DE": "gsg",
            "sgn-DK": "dsl",
            "sgn-ES": "ssp",
            "sgn-FR": "fsl",
            "sgn-GB": "bfi",
            "sgn-GR": "gss",
            "sgn-IE": "isg",
            "sgn-IT": "ise",
            "sgn-JP": "jsl",
            "sgn-MX": "mfs",
            "sgn-NI": "ncs",
            "sgn-NL": "dse",
            "sgn-NO": "nsl",
            "sgn-PT": "psr",
            "sgn-SE": "swl",
            "sgn-US": "ase",
            "sgn-ZA": "sfs",
            "zh-cmn": "cmn",
            "zh-gan": "gan",
            "zh-guoyu": "cmn",
            "zh-hakka": "hak",
            "zh-min-nan": "nan",
            "zh-nan": "nan",
            "zh-wuu": "wuu",
            "zh-xiang": "hsn",
            "zh-yue": "yue",
        }

    @staticmethod
    def get_supported_discord_codes() -> list[str]:
        """
        Get the Discord locale codes supported by Discord.

        See Pycord discord.commands.core valid_locales (not public)
        See <https://discord.com/developers/docs/reference#locales>

        Returns:
            list[str]: The list of Discord locale codes supported by Discord.
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
    def get_discord_code_mapping() -> dict[str, str]:
        """
        Get the mapping of BCP 47 language tag to Discord locale code.

        Returns:
            dict[str, str]: The mapping of BCP 47 language tag to Discord locale code.
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

        return {v: k for k, v in cls.get_discord_code_mapping().items()}

    @staticmethod
    def to_bcp_47_case(*, tag: str) -> str:
        """
        Convert language tag string to BCP 47 letter case.

        * language subtag: all lowercase. For example, zh.
        * script subtag: first letter uppercase. For example, Latn.
        * region subtag: all uppercase. For example, TW.
        * variant subtags: all lowercase. For example, wadegile.

        Parameters:
            tag (str): BCP 47 language tag string.

        Returns:
            str: BCP 47 language tag string with BCP 47 letter case.
        """

        tag_lower_subtags: list[str] = tag.lower().split("-")
        tag_bcp_47_case_subtags: list[str] = []

        for index, subtag in enumerate(tag_lower_subtags):
            if index > 0 and tag_lower_subtags[index - 1] == "x":
                # When the previous segment is x, it is a private subtag and
                # should be lowercase
                tag_bcp_47_case_subtags.append(subtag.lower())
            elif len(subtag) == 2 and index > 0:
                # BCP 47 region subtag
                tag_bcp_47_case_subtags.append(subtag.upper())
            elif len(subtag) == 4 and index > 0:
                # BCP 47 script subtag
                tag_bcp_47_case_subtags.append(subtag.title())
            else:
                # Use lowercase for other cases
                tag_bcp_47_case_subtags.append(subtag.lower())

        return "-".join(tag_bcp_47_case_subtags)

    @classmethod
    def to_bcp_47(cls, *, tag: str) -> str:
        """
        Normalize language tag string to BCP 47 language tag string, with
        letter case formatting and deprecated code replacements (for example,
        zh-min-nan => nan).

        Parameters:
            tag (str): Unnormalized BCP 47 language tag string.

        Returns:
            str: Normalized BCP 47 language tag string.
        """

        tag = tag.lower()

        for k, v in cls.get_bcp_47_prefix_mapping().items():
            if tag.startswith(k):
                tag = v + tag.removeprefix(k)

                break

        return cls.to_bcp_47_case(tag=tag)

    @classmethod
    def is_supported_discord_code(cls, *, code: str) -> bool:
        """
        Check if the given code is a supported Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            bool: Whether the given code is a supported Discord locale code.
        """

        return code in cls.get_supported_discord_codes()

    @classmethod
    def get_discord_code(cls, *, tag: str) -> str | None:
        """
        Get the Discord locale code from BCP 47 language tag.

        Parameters:
            tag (str): BCP 47 language tag.

        Returns:
            (str | None): the Discord locale code of the BCP 47 language tag.\
                Return None when there's no corresponding supported Discord\
                locale code.
        """

        code = cls.get_discord_code_mapping().get(tag, tag)

        if cls.is_supported_discord_code(code=code):
            return code

        return None

    @classmethod
    def get_from_discord_code(cls, *, code: str) -> str:
        """
        Get the BCP 47 language tag from Discord locale code.

        Parameters:
            code (str): Discord locale code.

        Returns:
            str: the BCP 47 language tag of the Discord locale code.
        """

        return cls.get_discord_code_to_bcp_47_mapping().get(code, code)


class SystemMessage:
    """
    The SystemMessage class deals with fetching and processing of system\
        messages.
    """

    _use_lang: str | None = None
    """
    _use_lang (str|None): The language tag of the language for the system\
        message to use.
    """

    _in_lang: str | None = None
    """
    _in_lang (str|None): The language tag of the language that the system\
        message actually used.
    """

    def __init__(
        self,
        key: str,
        params: list,
        use_lang: LanguageTag | None,
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

        self._use_lang = lang_tag

    def get_lang(self) -> str:
        """
        Get the final language tag of the language that the message used or\
            falls back to.

        Returns:
            str: Description of return value.
        """

        return self._use_lang or self._in_lang or ""
