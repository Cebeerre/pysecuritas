# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import unittest

import pytest
import responses

from pysecuritas.core.session import Session, BASE_URL, ConnectionException


class TestSession(unittest.TestCase):
    """
    Test suite for session
    """

    def test_basic_configuration(self) -> None:
        """
        Tests session basic configurations
        """

        session = Session("u1", "p1", "i1", "c1", "l1", "s1")
        self.assertEqual("u1", session.username)
        self.assertEqual("p1", session.password)
        self.assertEqual("i1", session.installation)
        self.assertEqual("c1", session.country)
        self.assertEqual("l1", session.lang)
        self.assertEqual("s1", session.sensor)
        self.assertEqual(30, session.timeout)
        session.set_timeout(60)
        self.assertEqual(60, session.timeout)

    def test_build_payload(self) -> None:
        """
        Tests building payload for performing actions against the api
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
        self.assertEqual({"Country": session.country, "user": session.username,
                          "pwd": session.password, "lang": session.lang, "hash": None, "callby": "AND_61",
                          "numinst": "i1", "panel": "SDVFAST", "cust1": "v1"},
                         session.build_payload(cust1="v1"))

    def test_get_or_create_session(self):
        """
        Tests creating a session and getting the created one
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
        self.assertEqual(session.get_or_create_session(), session.get_or_create_session())

    @responses.activate
    def test_invalid_connect_status(self):
        """
        Tests an invalid connection attempt with NOK result
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
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

        session = Session("u1", "p1", "i1", "c1", "l1")
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES></PET>'
        )

        with pytest.raises(ConnectionException):
            session.connect()

    @responses.activate
    def test_validate_connection(self):
        """
        Tests that a connection was established
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
        responses.add(
            responses.GET,
            BASE_URL,
            status=200,
            body='<?xml version="1.0" encoding="UTF-8"?><PET><RES>OK</RES><HASH>11111111111</HASH></PET>'
        )

        with pytest.raises(ConnectionException):
            session.validate_connection()

        session.connect()
        self.assertEqual("11111111111", session.login_hash)

    @responses.activate
    def test_valid_connect(self):
        """
        Tests an valid connection attempt
        """

        session = Session("u1", "p1", "i1", "c1", "l1")
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

        session = Session("u1", "p1", "i1", "c1", "l1")
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

        with Session("u1", "p1", "i1", "c1", "l1") as session:
            pass
