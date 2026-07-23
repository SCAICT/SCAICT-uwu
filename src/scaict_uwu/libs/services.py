"""
Module for service container.
"""

# Future statements
from __future__ import annotations

# Standard imports
from typing import Any, Callable, Self


class CannotReplaceActiveServiceError(Exception):
    """
    Error thrown when trying to replace an already active service.
    """

    def __init__(self, *, name: str):
        formatted_message = f"Cannot replace an active service: {name}"

        super().__init__(formatted_message)


class NoSuchServiceError(Exception):
    """
    Error thrown when the requested service is not known.
    """

    def __init__(self, *, name: str):
        formatted_message = f"No such service: {name}"

        super().__init__(formatted_message)


class Service:
    """
    Service instantiators and locators.
    """

    def __init__(self, *, name: str, instantiator: Callable[[ServiceContainer], Any]):
        """
        Parameters:
            name (str): Identifier of the service.
            instantiator (Callable[[ServiceContainer], Any]): Instantiator of
                the service.
        """

        self.name: str = name
        """
        Identifier of the service.
        """

        self._instantiator: Callable[[ServiceContainer], Any] = instantiator
        """
        Instantiator of the service.
        """

        self._instance: Any = None
        """
        Instance of the service.
        """

    @property
    def is_active(self) -> bool:
        """
        Whether the service is active or not.

        Returns:
            bool:
        """

        return self._instance is not None

    def redefine_instantiator(
        self, *, instantiator: Callable[[ServiceContainer], Any]
    ) -> None:
        """
        Parameters:
            instantiator (Callable[[ServiceContainer], Any])
        """

        if self.is_active:
            raise CannotReplaceActiveServiceError(name=self.name)

        self._instantiator = instantiator

    def get_instance(self, *, services: ServiceContainer) -> Any:
        """
        Get the instance of the service.
        If the service is not active, activate it and get its instance.

        Parameters:
            service (ServiceContainer): The service container instance for
                dependency resolution.

        Returns:
            Any: The instance of the service.
        """

        if self._instance is None:
            self._instance = self._instantiator(services)

        return self._instance


class ServiceAlreadyDefinedError(Exception):
    """
    Error thrown when a service was already defined, but the caller expected it to not exist.
    """

    def __init__(self, *, name: str):
        formatted_message = f"Service already defined: {name}"

        super().__init__(formatted_message)


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
