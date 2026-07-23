"""
Module for SCAICT-uwu service container.
"""

# Future statements
from __future__ import annotations

# Third-party imports
import discord

# Local imports
import scaict_uwu.core.config
import scaict_uwu.libs.language
import scaict_uwu.libs.services


class Services(scaict_uwu.libs.services.ServiceContainer):
    """
    Service instantiators and locators for SCAICT-uwu core services.
    """

    def __init__(self):
        super().__init__()

        self.apply_wiring(
            services={
                "scaict_uwu.core.config.Config": scaict_uwu.libs.services.Service(
                    name="Config", instantiator=self._init_config
                ),
                "scaict_uwu.core.config.ConfigFactory": scaict_uwu.libs.services.Service(
                    name="ConfigFactory", instantiator=self._init_config_factory
                ),
                "DiscordBot": scaict_uwu.libs.services.Service(
                    name="DiscordBot", instantiator=self._init_discord_bot
                ),
                "scaict_uwu.libs.language.LanguageTagFactory": scaict_uwu.libs.services.Service(
                    name="LanguageTagFactory",
                    instantiator=self._init_language_tag_factory,
                ),
            }
        )

    @staticmethod
    def _init_config(
        services: scaict_uwu.libs.services.ServiceContainer,
    ) -> scaict_uwu.core.config.Config:
        return services.get(name="scaict_uwu.core.config.ConfigFactory").get()

    @staticmethod
    def _init_config_factory(
        services: scaict_uwu.libs.services.ServiceContainer,
    ) -> scaict_uwu.core.config.ConfigFactory:
        return scaict_uwu.core.config.ConfigFactory()

    @staticmethod
    def _init_discord_bot(
        services: scaict_uwu.libs.services.ServiceContainer,
    ) -> discord.Bot:
        intents: discord.Intents = discord.Intents.default()

        intents.members = True
        intents.message_content = True

        return discord.Bot(intents=intents)

    @staticmethod
    def _init_language_tag_factory(
        services: scaict_uwu.libs.services.ServiceContainer,
    ) -> scaict_uwu.libs.language.LanguageTagFactory:
        return scaict_uwu.libs.language.LanguageTagFactory()
