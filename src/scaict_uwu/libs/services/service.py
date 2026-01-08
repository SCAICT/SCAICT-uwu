"""
Module for service.
"""

# Standard imports
# Prevents runtime evaluation of type hints
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

# Local imports
from .errors.cannot_replace_active_service_error import CannotReplaceActiveServiceError

# Conditional imports
if TYPE_CHECKING:
    from .container import ServiceContainer


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
