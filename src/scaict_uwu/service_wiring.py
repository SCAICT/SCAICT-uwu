"""
Module for SCAICT-uwu default service implementations.
"""

# Standard imports
from typing import Callable

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
        "LanguageTagFactory": _get_language_tag_factory,
    }


def _get_config(services: Services, /) -> Config:
    return services.get_config_factory().get()


def _get_config_factory(services: Services, /) -> ConfigFactory:
    return ConfigFactory()


def _get_language_tag_factory(services: Services, /) -> LanguageTagFactory:
    return LanguageTagFactory()
