"""
Unit test for Service using unittest.
"""

# Standard imports
import unittest

# Local imports
from scaict_uwu.libs.services.container import ServiceContainer
from scaict_uwu.libs.services.errors.cannot_replace_active_service_error import (
    CannotReplaceActiveServiceError,
)
from scaict_uwu.libs.services.service import Service


class MockService:
    def __init__(self, name: str):
        self.name: str = name


class TestService(unittest.TestCase):
    service_container: ServiceContainer | None

    def setUp(self) -> None:
        self.service_container = ServiceContainer()

        self.service_container.define_service(
            service=Service(name="MockService", instantiator=self._init_mock_service)
        )

    def tearDown(self) -> None:
        self.service_container = None

    @staticmethod
    def _init_mock_service(services: ServiceContainer) -> MockService:
        return MockService(name="MockService")

    @staticmethod
    def _init_mock_service3(services: ServiceContainer) -> MockService:
        return MockService(name="MockService3")

    def test_name(self) -> None:
        service_container: ServiceContainer = self.service_container
        service: Service = service_container.get(name="MockService")

        self.assertEqual(service.name, "MockService")

    def test_is_active(self) -> None:
        service_container = self.service_container
        service: Service = service_container.services["MockService"]

        self.assertFalse(service.is_active)

        service.get_instance(services=service_container)
        service = service_container.services["MockService"]

        self.assertTrue(service.is_active)

    def test_redefine_instantiator(self) -> None:
        service_container: ServiceContainer = self.service_container

        service_container.define_service(
            service=Service(name="MockService3", instantiator=self._init_mock_service)
        )

        service_container.redefine_service_instantiator(
            name="MockService3", instantiator=self._init_mock_service3
        )

        self.assertTrue(service_container.has_service(name="MockService3"))

        service3: MockService = service_container.get(name="MockService3")

        self.assertEqual(service3.name, "MockService3")

        with self.assertRaises(CannotReplaceActiveServiceError):
            service_container.redefine_service_instantiator(
                name="MockService3", instantiator=self._init_mock_service
            )

    def test_get_instance(self) -> None:
        service_container: ServiceContainer = self.service_container
        service: Service = service_container.services["MockService"]

        self.assertIsInstance(
            service.get_instance(services=service_container), MockService
        )


if __name__ == "__main__":
    unittest.main()
