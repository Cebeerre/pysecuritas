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

from pysecuritas.core.utils import handle_response, clean_response


class TestUtils(unittest.TestCase):
    """
    Test suite for utils file
    """

    def test_clean_response(self):
        """
        Tests response cleaning
        """
        response = {"PET": {"RES": "OK", "IN": {"c2": "v3"}, "BLOQ": "B1"}}
        response = clean_response(response)
        self.assertEqual({"RES": "OK", "IN": {"c2": "v3"}}, response)

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
            body='<PET>correct</PET>'
        )

        self.assertEqual("correct", handle_response(requests.get("https://securitas.dummy.com")))
