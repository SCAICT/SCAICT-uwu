"""
Module for SCAICT-uwu service locator.
"""

# Third-party imports
import discord

# Local imports
from .config.config import Config
from .config.factory import ConfigFactory
from .libs.language.language_tag_factory import LanguageTagFactory
from .libs.services.container import ServiceContainer


class Services(ServiceContainer):
    """
    Service locator for SCAICT-uwu core services.

    Refer to service_wiring.py for the default implementations.
    """

    # Service helper functions

    def get_config(self) -> Config:
        return self.get_service(name="Config")

    def get_config_factory(self) -> ConfigFactory:
        return self.get_service(name="ConfigFactory")

    def get_discord_bot(self) -> discord.Bot:
        return self.get_service(name="DiscordBot")

    def get_discord_intents(self) -> discord.Intents:
        return self.get_service(name="DiscordIntents")

    def get_language_tag_factory(self) -> LanguageTagFactory:
        return self.get_service(name="LanguageTagFactory")
