# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest

from pysecuritas.core.commands import ALARM_OPS, get_available_commands, API_OPS


class TestCommands(unittest.TestCase):
    """
    Test suite for commands file
    """

    def test_available_commands(self) -> None:
        """
        Tests that all available commands are provided to the cli
        """

        available_commands = get_available_commands()
        for command in ALARM_OPS:
            self.assertTrue(command in available_commands)

        for command in API_OPS:
            self.assertTrue(command in available_commands)
