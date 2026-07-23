"""
Config
"""

# Future statements
from __future__ import annotations

# Standard imports
import sys


class Config:
    """
    Config object
    """

    def __init__(self):
        self.options: dict = {}

    def get_option(self, name: str):
        if name in self.options:
            return self.options[name]

        sys.exit("NoSuchOptionExpection")


class ConfigFactory:
    """
    Config factory
    """

    def get(self) -> Config:
        return Config()


class ConfigNames:
    """
    Config names
    """


class ConfigSchema:
    """
    Config schema
    """
