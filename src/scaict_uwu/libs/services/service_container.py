"""
Module for service container.
"""

# Standard imports
import sys
from typing import Callable


class ServiceContainer:
    """
    Service locator for services.
    """

    _services: dict = {}
    """
    """

    _service_instantiators: dict[str, Callable] = {}
    """
    """

    _services_being_created: dict[str, bool] = {}
    """
    """

    # Wiring module functions

    def load_wiring_module(self, *, module) -> None:
        try:
            self.apply_wiring(service_instantiators=module.get_wiring())
        except AttributeError:
            sys.exit("InvalidWiringModuleException")

    def load_wiring_modules(self, *, modules: list) -> None:
        for module in modules:
            self.load_wiring_module(module=module)

    def apply_wiring(self, *, service_instantiators: dict[str, Callable]) -> None:
        for name, instantiator in service_instantiators.items():
            self.define_instantiator(name=name, instantiator=instantiator)

    # Service instantiator functions

    def get_instantiator_names(self) -> list:
        # Convert dict_keys to list
        return list(self._service_instantiators.keys())

    def has_instantiator(self, *, name: str) -> bool:
        return name in self._service_instantiators

    def define_instantiator(self, *, name: str, instantiator: Callable) -> None:
        if self.has_instantiator(name=name):
            sys.exit(f"ServiceAlreadyDefinedException {name}")

        self._service_instantiators[name] = instantiator

    def redefine_instantiator(self, *, name: str, instantiator: Callable) -> None:
        if not self.has_instantiator(name=name):
            sys.exit(f"NoSuchServiceException {name}")

        if name in self._services:
            sys.exit(f"CannotReplaceActiveServiceException {name}")

        self._service_instantiators[name] = instantiator

    # Service functions

    def create_service(self, /, name: str):
        if not self.has_instantiator(name=name):
            sys.exit("NoSuchServiceException $name")

        if name in self._services_being_created:
            sys.exit(
                "RecursiveServiceDependencyException "
                + "Circular dependency when creating service!"
            )

        self._services_being_created[name] = True

        return self._service_instantiators[name](services=self)

    def get_service(self, *, name: str):
        if name not in self._services:
            self._services[name] = self.create_service(name=name)

        return self._services[name]
