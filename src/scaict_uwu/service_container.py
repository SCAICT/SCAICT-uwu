"""
Module for SCAICT-uwu service locator.
"""

# Standard imports
import sys
from typing import Callable

# Local imports
from .core.config.config import Config
from .core.config.config_factory import ConfigFactory
from .libs.language.language_tag_factory import LanguageTagFactory


class ServiceContainer:
    """
    Service locator for SCAICT-uwu core services.

    Refer to service_wiring.py for the default implementations.
    """

    _services: dict = {}
    """
    """

    _service_instantiators: dict = {}
    """
    """

    _services_being_created: dict = {}
    """
    """

    def load_wiring_module(self, module) -> None:
        try:
            self.apply_wiring(module.get_wiring())
        except AttributeError:
            sys.exit("InvalidWiringModuleException")

    def load_wiring_modules(self, modules: list) -> None:
        for module in modules:
            self.load_wiring_module(module)

    def apply_wiring(self, service_instantiators) -> None:
        for name, instantiator in service_instantiators:
            self.define_service(name, instantiator)

    def get_service_names(self) -> list:
        # Convert dict_keys to list
        return list(self._service_instantiators.keys())

    def has_service(self, name: str) -> bool:
        return name in self._service_instantiators

    def define_service(self, name: str, instantiator: Callable) -> None:
        if self.has_service(name):
            sys.exit("ServiceAlreadyDefinedException $name")

        self._service_instantiators[name] = instantiator

    def redefine_service(self, name: str, instantiator: Callable) -> None:
        if not self.has_service(name):
            sys.exit("NoSuchServiceException $name")

        if name in self._services:
            sys.exit("CannotReplaceActiveServiceException $name")

        self._service_instantiators[name] = instantiator

    def create_service(self, name: str):
        if not self.has_service(name):
            sys.exit("NoSuchServiceException $name")

        if name in self._services_being_created:
            sys.exit(
                "RecursiveServiceDependencyException "
                + "Circular dependency when creating service!"
            )

        self._services_being_created[name] = True

        return self._service_instantiators[name](self)

    def get_service(self, name: str):
        if name not in self._services:
            self._services[name] = self.create_service(name)

        return self._services[name]

    # Service helper functions

    def get_config(self) -> Config:
        return self.get_service("Config")

    def get_config_factory(self) -> ConfigFactory:
        return self.get_service("ConfigFactory")

    def get_language_tag_factory(self) -> LanguageTagFactory:
        return self.get_service("LanguageTagFactory")
