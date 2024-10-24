"""
This is the module for the class for all languages.
"""


class Language:
    """
    The Language class deals with language data.
    """

    def get_bcp_47_lang_tag(self) -> str | None:
        pass

    def get_bcp_47_lang_subtag(self) -> str | None:
        pass

    def get_iso_639_lang_code(self) -> str | None:
        pass

    def get_bcp_47_script_subtag(self) -> str | None:
        pass

    def get_bcp_47_region_subtag(self) -> str | None:
        pass

    def get_bcp_47_variant_subtags(self) -> list | None:
        pass

    def get_bcp_47_private_subtags(self) -> list | None:
        pass

    def get_writing_mode(self) -> str | None:
        pass

    def get_writing_mode_dir(self) -> str | None:
        pass

    def get_writing_mode_prop(self) -> str | None:
        pass

    def get_lang_fallbacks(self) -> list | None:
        pass
