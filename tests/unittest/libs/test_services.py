"""
Unit test for services using unittest.
"""

# Future statements
from __future__ import annotations

# Standard imports
import unittest

# Local imports
from scaict_uwu.libs.services import (
    CannotReplaceActiveServiceError,
    NoSuchServiceError,
    Service,
    ServiceAlreadyDefinedError,
    ServiceContainer,
)


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


class TestServiceContainer(unittest.TestCase):
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

    def test_apply_wiring(self) -> None:
        service_container: ServiceContainer = self.service_container

        service_container.apply_wiring(
            services={
                "MockService2": Service(
                    name="MockService2", instantiator=self._init_mock_service
                )
            }
        )

        self.assertTrue(service_container.has_service(name="MockService2"))

    def test_has_service(self) -> None:
        service_container: ServiceContainer = self.service_container

        self.assertTrue(service_container.has_service(name="MockService"))

    def test_define_service(self) -> None:
        service_container: ServiceContainer = self.service_container

        service_container.define_service(
            service=Service(name="MockService3", instantiator=self._init_mock_service)
        )

        self.assertTrue(service_container.has_service(name="MockService3"))

        with self.assertRaises(ServiceAlreadyDefinedError):
            service_container.define_service(
                service=Service(
                    name="MockService3", instantiator=self._init_mock_service
                )
            )

    def test_redefine_service(self) -> None:
        service_container: ServiceContainer = self.service_container

        with self.assertRaises(NoSuchServiceError):
            service_container.redefine_service_instantiator(
                name="MockService4", instantiator=self._init_mock_service
            )

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

    def test_get(self) -> None:
        service_container: ServiceContainer = self.service_container

        self.assertIsInstance(service_container.get(name="MockService"), MockService)


if __name__ == "__main__":
    unittest.main()
