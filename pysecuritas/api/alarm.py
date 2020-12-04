# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

from typing import Dict

from pysecuritas.api.installation import Installation, DEFAULT_TIMEOUT


def get_available_commands() -> Dict:
    """
    Returns all available commands
    """

    return {
        "ARM": "arm all sensors (inside)",
        "ARMDAY": "arm in day mode (inside)",
        "ARMNIGHT": "arm in night mode (inside)",
        "PERI": "arm (only) the perimeter sensors",
        "DARM": "disarm everything (not the annex)",
        "ARMANNEX": "arm the secondary alarm",
        "DARMANNEX": "disarm the secondary alarm",
        "EST": "return the panel status"
    }


class Alarm(Installation):
    """
    The entrypoint to perform any action on an alarm such as arm and disarm
    """

    def __init__(self, session, timeout=DEFAULT_TIMEOUT):
        """
        Initializes alarm api
        """

        super(Alarm, self).__init__(session, timeout)

    def execute_command(self, command) -> Dict:
        """
        Executes a command

        :param command command to be executed

        :return: the result from the operation
        """

        if command == "ARM":
            return self.activate_total_mode()

        if command == "ARMDAY":
            return self.activate_day_mode()

        if command == "ARMNIGHT":
            return self.activate_night_mode()

        if command == "PERI":
            return self.activate_perimeter_mode()

        if command == "DARM":
            return self.disconnect()

        if command == "ARMANNEX":
            return self.activate_secondary_mode()

        if command == "DARMANNEX":
            return self.disconnect_secondary()

        if command == "EST":
            return self.get_status()

    def activate_total_mode(self) -> Dict:
        """
        Activates alarm in total mode (all sensors)
        """

        return self.async_request("ARM")

    def activate_secondary_mode(self) -> Dict:
        """
        Activates secondary alarm
        """

        return self.async_request("ARMANNEX")

    def activate_day_mode(self) -> Dict:
        """
        Activates alarm in day mode (only sensors configured for day mode will be activated)
        """

        return self.async_request("ARMDAY")

    def activate_night_mode(self) -> Dict:
        """
        Activates alarm in night mode (only sensors configured for night mode will be activated)
        """

        return self.async_request("ARMNIGHT")

    def activate_perimeter_mode(self) -> Dict:
        """
        Activates alarm in perimeter mode (only sensors configured for exterior mode will be activated)
        """

        return self.async_request("PERI")

    def get_status(self) -> Dict:
        """
        Retrieves current alarm status
        """

        return self.async_request("EST")

    def disconnect(self) -> Dict:
        """
        Disconnects the alarm
        """

        return self.async_request("DARM")

    def disconnect_secondary(self) -> Dict:
        """
        Disconnects the secondary alarm
        """

        return self.async_request("DARMANNEX")
