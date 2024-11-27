"""
Module for SCAICT-uwu service locator.
"""

# Standard imports
import importlib
import sys


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

    def load_wiring_files(self, wiring_modules: list) -> None:
        for module_name in wiring_modules:
            module = importlib.import_module(module_name)
            self.apply_wiring(module.get_wiring())

    def apply_wiring(self, service_instantiators) -> None:
        for name, instantiator in service_instantiators:
            self.define_service(name, instantiator)

    def get_service_names(self) -> list:
        # Convert dict_keys to list
        return list(self._service_instantiators.keys())

    def has_service(self, name: str) -> bool:
        return name in self._service_instantiators

    def define_service(self, name: str, instantiator) -> None:
        if self.has_service(name):
            sys.exit("ServiceAlreadyDefinedException $name")

        self._service_instantiators[name] = instantiator

    def redefine_service(self, name: str, instantiator) -> None:
        if not self.has_service(name):
            sys.exit("NoSuchServiceException $name")

        if name in self._services:
            sys.exit("CannotReplaceActiveServiceException $name")

        self._service_instantiators[name] = instantiator

    def create_service(self, name: str):
        if not self.has_service(name):
            sys.exit("NoSuchServiceException $name")

        if not name in self._services_being_created:
            sys.exit(
                "RecursiveServiceDependencyException "
                + "Circular dependency when creating service!"
            )

        self._services_being_created[name] = True

        service = self._service_instantiators[name](self)

        return service

    def get_service(self, name: str):
        if not name in self._services:
            self._services[name] = self.create_service(name)

        return self._services[name]

    # Service helper functions

    def get_config(self):
        return self.get_service("Config")

    def get_language_tag(self):
        return self.get_service("LanguageTag")

    def get_language_tag_factory(self):
        return self.get_service("LanguageTagFactory")
