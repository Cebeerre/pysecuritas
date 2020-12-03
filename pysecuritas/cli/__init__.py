# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

from pysecuritas.cli.cli_command import CLICommand


def run_command(args=None) -> None:
    """
    Runs a command with the provided arguments

    :param args: arguments to execute the operation (including operation to be performed)
    """

    cli_cmd = CLICommand()
    cli_cmd.parse(args)
    cli_cmd.run()
    cli_cmd.pretty_print()
