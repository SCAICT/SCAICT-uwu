"""
Module for SCAICT-uwu service container.
"""

# Future statements
from __future__ import annotations

# Third-party imports
import discord

# Local imports
from scaict_uwu.core.config import (
    Config,
    ConfigFactory,
)
from scaict_uwu.libs.language import (
    LanguageTagFactory,
)
from scaict_uwu.libs.services import (
    Service,
    ServiceContainer,
)


class Services(ServiceContainer):
    """
    Service instantiators and locators for SCAICT-uwu core services.
    """

    def __init__(self):
        super().__init__()

        self.apply_wiring(
            services={
                "Config": Service(name="Config", instantiator=self._init_config),
                "ConfigFactory": Service(
                    name="ConfigFactory", instantiator=self._init_config_factory
                ),
                "DiscordBot": Service(
                    name="DiscordBot", instantiator=self._init_discord_bot
                ),
                "LanguageTagFactory": Service(
                    name="LanguageTagFactory",
                    instantiator=self._init_language_tag_factory,
                ),
            }
        )

    @staticmethod
    def _init_config(services: ServiceContainer) -> Config:
        return services.get(name="ConfigFactory").get()

    @staticmethod
    def _init_config_factory(services: ServiceContainer) -> ConfigFactory:
        return ConfigFactory()

    @staticmethod
    def _init_discord_bot(services: ServiceContainer) -> discord.Bot:
        intents: discord.Intents = discord.Intents.default()

        intents.members = True
        intents.message_content = True

        return discord.Bot(intents=intents)

    @staticmethod
    def _init_language_tag_factory(services: ServiceContainer) -> LanguageTagFactory:
        return LanguageTagFactory()
