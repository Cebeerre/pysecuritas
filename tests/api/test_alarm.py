# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest

import responses

from pysecuritas.api.alarm import Alarm
from pysecuritas.core.session import Session, BASE_URL


class TestAlarm(unittest.TestCase):

    @responses.activate
    def test_command_parameters(self):
        """
        Tests all requests base action parameters
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        alarm = Alarm(session, 10)
        _self = self

        def assert_command(action):
            """
            asserts calls to a specific action

            :param action action being performed
            """

            responses.reset()
            responses.add(
                responses.GET,
                BASE_URL,
                status=200,
                body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
            )

            _self.assertEqual({"RES": "OK", "HASH": "11111111111"}, alarm.execute_command(action))
            _self.assertGreaterEqual(len(responses.calls), 2)
            _self.assertTrue(action + "1" in responses.calls[0].request.params["request"])
            _self.assertTrue(action + "2" in responses.calls[1].request.params["request"])

        assert_command("ARM")
        assert_command("ARMDAY")
        assert_command("ARMNIGHT")
        assert_command("PERI")
        assert_command("DARM")
        assert_command("ARMANNEX")
        assert_command("DARMANNEX")
        assert_command("EST")
