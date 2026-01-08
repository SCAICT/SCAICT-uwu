"""
Module for service container.
"""

# Standard imports
# Prevents runtime evaluation of type hints
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Self

# Local imports
from .errors.no_such_service_error import NoSuchServiceError
from .errors.service_already_defined_error import ServiceAlreadyDefinedError

# Conditional imports
if TYPE_CHECKING:
    from .service import Service


class ServiceContainer:
    """
    Service container for services instantiators and locators.
    """

    def __init__(self):
        self.services: dict[str, Service] = {}
        """
        Created services.
        """

    def apply_wiring(self, *, services: dict[str, Service]) -> None:
        """
        Parameters:
            services (dict[str, Service]):
        """

        for service in services.values():
            self.define_service(service=service)

    def has_service(self, *, name: str) -> bool:
        """
        Returns:
            bool:
        """

        return name in self.services

    def define_service(self, *, service: Service) -> None:
        """
        Parameters:
            service (Service):
        """

        name: str = service.name

        if self.has_service(name=name):
            raise ServiceAlreadyDefinedError(name=name)

        self.services[name] = service

    def redefine_service_instantiator(
        self, *, name: str, instantiator: Callable[[Self], Any]
    ) -> None:
        """
        Parameters:
            name (str):
            instantiator (Callable[[Self], Any]):
        """

        if not self.has_service(name=name):
            raise NoSuchServiceError(name=name)

        self.services[name].redefine_instantiator(instantiator=instantiator)

    def get(self, *, name: str) -> Any:
        """
        Parameters:
            name (str):

        Returns:
            Any:
        """

        if not self.has_service(name=name):
            raise NoSuchServiceError(name=name)

        return self.services[name].get_instance(services=self)
