"""
Module for SCAICT-uwu default service implementations.
"""

from .service_container import ServiceContainer


def get_wiring() -> dict:
    """
    Get the service implementation functions.
    """
    return {"Config": get_config}


def get_config(service_container: ServiceContainer):
    pass
