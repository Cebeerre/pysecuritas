# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest
from pyexpat import ExpatError

import pytest
import requests
import responses
from requests import HTTPError

from pysecuritas.core.session import Session, handle_response, get_response_value, BASE_URL, ConnectionException


class TestCommands(unittest.TestCase):
    """
    Test suite for commands file
    """

    def test_basic_configuration(self) -> None:
        """
        Tests session basic configurations
        """

        session = Session().set_username("u1").set_password("p1").set_installation("i1").set_country(
            "c1").set_lang("l1")
        self.assertEqual("u1", session.username)
        self.assertEqual("p1", session.password)
        self.assertEqual("i1", session.installation)
        self.assertEqual("c1", session.country)
        self.assertEqual("l1", session.lang)
        self.assertEqual(30, session.timeout)
        session.set_timeout(60)
        self.assertEqual(60, session.timeout)

    def test_get_response_value(self):
        # test subset equals to original response
        response = {"PET": {"RES": "OK", "IN": {"c2": "v3"}}}
        result, subset = get_response_value(response)
        self.assertEqual("OK", result)
        self.assertEqual(response, subset)
        # test known subset
        result, subset = get_response_value(response, "PET", "IN")
        self.assertEqual({"c2": "v3"}, subset)
        # test unknown subset
        self.assertEqual((None, None), get_response_value(response, "PET", "OUT"))

    @responses.activate
    def test_unsuccessful_response(self):
        """
        Tests handling a response that is not 200
        """

        responses.add(
            responses.GET,
            "https://securitas.dummy.com",
            status=404
        )

        with pytest.raises(HTTPError):
            handle_response(requests.get("https://securitas.dummy.com"))

    @responses.activate
    def test_bad_response_xml(self):
        """
        Tests parsing a request with invalid xml syntax
        """

        responses.add(
            responses.GET,
            "https://securitas.dummy.com",
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><tag>unclosed'
        )

        with pytest.raises(ExpatError):
            handle_response(requests.get("https://securitas.dummy.com"))

    @responses.activate
    def test_successful_response_xml(self):
        """
        Tests parsing a request with correct xml syntax
        """

        responses.add(
            responses.GET,
            "https://securitas.dummy.com",
            status=200,
            body='<tag>correct</tag>'
        )

        self.assertEqual("correct", handle_response(requests.get("https://securitas.dummy.com"))["tag"])

    def test_get_or_create_session(self):
        """
        Tests creating a session and getting the created one
        """

        session = Session()
        self.assertEqual(session.get_or_create_session(), session.get_or_create_session())

    @responses.activate
    def test_invalid_connect_status(self):
        """
        Tests an invalid connection attempt with NOK result
        """

        session = Session().set_username("u1")
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>ERROR</RES></PET>'
        )

        with pytest.raises(ConnectionException):
            session.connect()

    @responses.activate
    def test_invalid_connect_no_hash(self):
        """
        Tests an invalid connection attempt without hash value in the response
        """

        session = Session().set_username("u1")
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES></PET>'
        )

        with pytest.raises(ConnectionException):
            session.connect()

    @responses.activate
    def test_valid_connect(self):
        """
        Tests an valid connection attempt
        """

        session = Session().set_username("u1")
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        session.connect()
        self.assertEqual("11111111111", session.login_hash)

    @responses.activate
    def test_invalid_close(self):
        """
        Tests an invalid close attempt
        """

        session = Session().set_username("u1")
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>ERROR</RES></PET>'
        )

        with pytest.raises(ConnectionException):
            session.close()

    @responses.activate
    def test_valid_close(self):
        """
        Tests an valid close attempt
        """

        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        with Session().set_username("u1") as session:
            pass
