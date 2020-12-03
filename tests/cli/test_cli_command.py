# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest

from pysecuritas.cli.cli_command import CLICommand


class TestCLICommand(unittest.TestCase):
    """
    Test suite for cli operations
    """

    def test_arguments(self) -> None:
        """
        Tests parsing of arguments
        """

        cli_command = CLICommand()
        arguments = ["-u", "u1", "-p", "p1", "-i", "i1", "-c", "c1", "-l", "l1", "-s", "s1", "command1"]
        cli_command.parse(arguments)
        self.assertEqual("u1", cli_command.args.username)
        self.assertEqual("p1", cli_command.args.password)
        self.assertEqual("i1", cli_command.args.installation)
        self.assertEqual("c1", cli_command.args.country)
        self.assertEqual("l1", cli_command.args.language)
        self.assertEqual("s1", cli_command.args.sensor)
        self.assertEqual("command1", cli_command.args.command)
