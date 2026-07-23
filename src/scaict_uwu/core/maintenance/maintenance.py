"""
This is the module for the abstract class for all maintenance scripts.
"""

# Future statements
from __future__ import annotations


class MaintenanceParameters:
    """
    Command line parameter handler for maintenance scripts.
    """

    __description: str
    """
    __description (str): Short description of what the script does.
    """

    def has_description(self) -> bool:
        """
        Check whether the script has description.

        Returns:
            bool
        """
        return self.__description != ""

    def get_description(self) -> str:
        """
        Get the short description of what the script does.

        Returns:
            str: The short description
        """
        return self.__description

    def set_description(self, text: str) -> None:
        """
        Set a short description of what the script does.

        Parameters:
            text (str)
        """
        self.__description = text

    def get_help(self) -> str:
        """
        Get help text.

        Returns:
            str
        """
        output: list = []

        # Description
        if self.has_description():
            output.append("")

        return "".join(output)


class MaintenanceScript:
    """
    Abstract class for all maintenance scripts.
    """

    _parameters: MaintenanceParameters
    """
    _parameters (MaintenanceParameters)
    """

    def __init__(self) -> None:
        """
        Default constructor. Child classes should call this *first* if
        implementing their own constructors.
        """
        self._parameters = MaintenanceParameters()
        self.add_default_params()

    def add_description(self, description: str) -> None:
        """
        Set description for maintenance scription.

        Parameters:
            description (str): The description to set.
        """
        self.get_parameters().set_description(description)

    def get_parameters(self) -> MaintenanceParameters:
        """
        Returns:
            MaintenanceParameters
        """
        return self._parameters

    def add_default_params(self) -> None:
        """
        TODO
        """

    def can_execute_without_config(self) -> bool:
        """
        Whether this script can run without config.

        Scripts that need to be able to run before installed should override\
        this to return true.

        Scripts that return true from this method will fail with a fatal error
        if attempt to access the database.

        Subclasses that override this method to return true should also\
        override get_db_type() to return self::DB_NONE.
        """
        return False

    def execute(self) -> bool:
        """
        Do the actual work. All child classes will need to implement this.

        Returns:
            bool: True for success, false for failure.
                Returning false for failure will cause\
                do_maintenance.py to exit the process with a non-zero exit\
                status.

        Raises:
            NotImplementedError: The method must be implemented in subclass.
        """
        # Abstract
        raise NotImplementedError
