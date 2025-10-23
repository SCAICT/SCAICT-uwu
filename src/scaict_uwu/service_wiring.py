"""
Module for SCAICT-uwu default service implementations.
"""

# Standard imports
from typing import Callable

# Third-party imports
import discord

# Local imports
from .core.config.config import Config
from .core.config.config_factory import ConfigFactory
from .libs.language.language_tag_factory import LanguageTagFactory
from .services import Services


def get_wiring() -> dict[str, Callable]:
    """
    Get the service instantiator functions.

    Returns:
        dict: A mapping of service names to their instantiator functions.
            Format: {"service_name": instantiator_function}
    """

    return {
        "Config": _get_config,
        "ConfigFactory": _get_config_factory,
        "DiscordBot": _get_discord_bot,
        "DiscordIntents": _get_discord_intents,
        "LanguageTagFactory": _get_language_tag_factory,
    }


def _get_config(*, services: Services) -> Config:
    return services.get_config_factory().get()


def _get_config_factory(*, services: Services) -> ConfigFactory:
    return ConfigFactory()


def _get_discord_bot(*, services: Services) -> discord.Bot:
    return discord.Bot(intents=services.get_discord_intents())


def _get_discord_intents(*, services: Services) -> discord.Intents:
    intents: discord.Intents = discord.Intents.default()

    intents.members = True
    intents.message_content = True

    return intents


def _get_language_tag_factory(*, services: Services) -> LanguageTagFactory:
    return LanguageTagFactory()
