"""
Config
"""

# Future statements
from __future__ import annotations

# Standard imports
import sys
import typing


class Config:
    """
    Config object
    """

    def __init__(self) -> None:
        self.options: dict = {}

    def get_option(self, name: str) -> typing.Any:
        """
        Parameters:
            name (str):

        Returns:
            typing.Any:
        """

        if name in self.options:
            return self.options[name]

        sys.exit("NoSuchOptionExpection")


class ConfigFactory:
    """
    Config factory
    """

    def get(self) -> Config:
        """
        Returns:
            scaict_uwu.core.config.Config:
        """

        return Config()


class ConfigNames:
    """
    Config names
    """


class ConfigSchema:
    """
    Config schema
    """
