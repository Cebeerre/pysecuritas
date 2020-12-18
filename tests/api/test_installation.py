# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest

import pytest
import requests
import responses

from pysecuritas.api.installation import handle_result, RequestException, Installation
from pysecuritas.core.session import BASE_URL, Session
from pysecuritas.core.utils import handle_response


class TestInstallation(unittest.TestCase):
    """
    Test suite for installation
    """

    @responses.activate
    def test_async_request_timeout(self):
        """
        Tests a request timeout
        """

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>WAIT</RES></PET>'
        )

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        installation = Installation(session, 1)
        self.assertIsNone(installation.async_request("DUMMY"))
        self.assertGreaterEqual(len(responses.calls), 2)

    @responses.activate
    def test_inf_request_timeout(self):
        """
        Tests a request timeout
        """

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><LIST><REG signaltype="1"></REG><REG signaltype="1"></REG></LIST></PET>'
        )

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        alarm = Installation(session, 1)
        self.assertIsNone(alarm.get_inf())
        self.assertGreaterEqual(len(responses.calls), 1)

    @responses.activate
    def test_inf_valid_request(self):
        """
        Tests a request timeout
        """

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><LIST><REG signaltype="16" idsignal="1"></REG><REG signaltype="16" idsignal="1"></REG></LIST></PET>'
        )

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        alarm = Installation(session, 1)
        self.assertEqual({"RES": "OK", "HASH": "11111111111"}, alarm.get_inf())
        self.assertGreaterEqual(len(responses.calls), 1)

    @responses.activate
    def test_async_valid_request(self):
        """
        Tests a valid request
        """

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        alarm = Installation(session, 1)
        self.assertEqual({"RES": "OK", "HASH": "11111111111"}, alarm.async_request("DUMMY"))
        self.assertGreaterEqual(len(responses.calls), 2)

    @responses.activate
    def test_handle_result(self):
        """
        Tests handling different result status
        """

        def assert_result(status):
            responses.reset()
            responses.add(
                responses.GET,
                BASE_URL,
                status=200,
                body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>' + status + '</RES><MSG>ERROR</MSG></PET>'
            )

            result = handle_response(requests.get(BASE_URL))

            return handle_result(result.get("RES"), result)

        with pytest.raises(RequestException):
            assert_result("ERROR")

        self.assertIsNone(assert_result("WAIT"))
        self.assertEqual({"RES": "OK", "MSG": "ERROR"}, assert_result("OK"))

    @responses.activate
    def test_command_parameters(self):
        """
        Tests all requests base action parameters
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        installation = Installation(session, 10)
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

            _self.assertEqual({"RES": "OK", "HASH": "11111111111"}, installation.execute_command(action))
            _self.assertEqual(len(responses.calls), 1)
            _self.assertTrue(action in responses.calls[0].request.params["request"])

        assert_command("ACT_V2")
        assert_command("SRV")
        assert_command("MYINSTALLATION")

    @responses.activate
    def test_get_installation_alias(self):
        """
        Tests getting the installation alias
        """

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><INSTALATION><ALIAS>alias</ALIAS></INSTALATION></PET>'
        )

        session = Session("u1", "p1", "i1", "c1", "l1")
        session.login_hash = "1"
        installation = Installation(session, 10)
        self.assertEqual("alias", installation.get_alias())
