# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest

import responses

from pysecuritas.cli.cli_command import CLICommand
from pysecuritas.core.session import BASE_URL


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

    @responses.activate
    def test_run_alarm_command(self) -> None:
        """
        Tests running a command from each api entity (alarm, installation, ...)
        """

        cli_command = CLICommand()
        arguments = ["-u", "u1", "-p", "p1", "-i", "i1", "-c", "c1", "-l", "l1", "-s", "s1", "ARM"]
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        cli_command.parse(arguments)
        cli_command.run()
        self.assertEqual({"RES": "OK", "HASH": "11111111111"}, cli_command.result)
        self.assertGreaterEqual(len(responses.calls), 3)
        self.assertTrue("ARM1" in responses.calls[1].request.params["request"])
        self.assertTrue("ARM2" in responses.calls[2].request.params["request"])

    @responses.activate
    def test_run_alarm_command(self) -> None:
        """
        Tests running a command from each api entity (alarm, installation, ...)
        """

        cli_command = CLICommand()
        arguments = ["-u", "u1", "-p", "p1", "-i", "i1", "-c", "c1", "-l", "l1", "-s", "s1", "ACT_V2"]
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        cli_command.parse(arguments)
        cli_command.run()
        self.assertEqual({"RES": "OK", "HASH": "11111111111"}, cli_command.result)
        self.assertEqual(len(responses.calls), 3)
        self.assertTrue("ACT_V2" in responses.calls[1].request.params["request"])
