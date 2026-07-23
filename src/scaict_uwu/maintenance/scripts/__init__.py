"""
Maintenance scripts
"""

# Future statements
from __future__ import annotations

# Local imports
import scaict_uwu.maintenance


class MaintenanceScriptUpdate(scaict_uwu.maintenance.MaintenanceScript):
    """
    Maintenance script to run database schema updates.

    Run all updaters.

    This is used when the database schema is modified and we need to apply patches.
    """

    def __init__(self) -> None:
        super().__init__()

        self.add_description("Database updater.")

    def execute(self) -> bool:
        return True
