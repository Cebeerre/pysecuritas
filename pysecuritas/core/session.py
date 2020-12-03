# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import json
import logging
from datetime import datetime
from typing import Dict

import requests
import xmltodict
from requests.adapters import HTTPAdapter
from urllib3 import Retry

log = logging.getLogger("pysecuritas")


def handle_response(response) -> Dict:
    """
    Raises exception if request was not successful or parses
    the xml response into a dictionary

    :param response http response to be validated and parsed

    :return: a parsed structured from the xml response
    """

    response.raise_for_status()

    return xmltodict.parse(response.text)


def get_response_value(response, *keys) -> (str, Dict):
    """
    Validates that a specific set of keys is in the response
    and returns response result as well as the combination of those keys

    :param response full response data
    :param keys keys to build a subset from the full response

    :return: the response result and the subset built
    """

    subset = response
    if len(keys):
        for k in keys:
            try:
                subset = subset[k]
            except (KeyError, TypeError):
                return None, None

    try:
        return response["PET"]["RES"], subset
    except (KeyError, TypeError):
        pass


# in seconds
DEFAULT_TIMEOUT = 30
BASE_URL = "https://mob2217.securitasdirect.es:12010/WebService/ws.do"


class Session:
    """
    A session will handle connectivity to interact with securitas installation and devices
    """

    def __init__(self):
        """
        Session initializer
        """

        self.username = None
        self.password = None
        self.country = None
        self.installation = None
        self.lang = None
        self.timeout = DEFAULT_TIMEOUT
        self.session = None
        self.login_hash = None
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

    def set_username(self, username: str):
        """
        Sets the value of `username`

        :return: self
        """

        self.username = username

        return self

    def set_password(self, password: str):
        """
        Sets the value of `password`

        :return: self
        """

        self.password = password

        return self

    def set_country(self, country: str):
        """
        Sets the value of `country`

        :return: self
        """

        self.country = country

        return self

    def set_installation(self, installation: str):
        """
        Sets the value of `installation`

        :return: self
        """

        self.installation = installation

        return self

    def set_lang(self, lang: str):
        """
        Sets the value of `installation`

        :return: self
        """

        self.lang = lang

        return self

    def set_timeout(self, timeout: int):
        """
        Sets the value of `timeout`

        :return: self
        """

        self.timeout = timeout

        return self

    def get_or_create_session(self):
        """
        Creates a new session to make requests or retrieves an existing one

        :return: a requests session
        """

        if not self.session:
            log.debug("Creating new session")
            self.session = requests.Session()
            self.session.mount("https://", HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))

        return self.session

    def generate_request_id(self):
        """
        Generates a new request id
        """

        return "AND_________________________" + self.username + datetime.now().strftime("%Y%m%d%H%M%S")

    def connect(self) -> None:
        """
        Connects to api by logging in and creating a new session
        """

        log.info("Connecting to securitas server")
        response = self.get({"Country": self.country,
                             "user": self.username,
                             "pwd": self.password,
                             "lang": self.lang, "request": "LOGIN",
                             "ID": self.generate_request_id()})

        result, login_hash = get_response_value(response, "PET", "HASH")
        if result != "OK" or not login_hash:
            log.error("Unable to login: %s", json.dumps(response))

            raise ConnectionException("Unable to login ")

        log.info("Connected to securitas server")
        self.login_hash = login_hash

    def get(self, payload) -> Dict:
        """
        Performs a GET request and returns a dictionary with the parsed response

        :param payload get request parameters

        :return: a parsed structured from the xml response
        """

        return handle_response(
            self.get_or_create_session().get(BASE_URL, params=payload, timeout=self.timeout))

    def post(self, payload) -> Dict:
        """
        Performs a POST request and returns a dictionary with the parsed response

        :param payload get request parameters

        :return: a parsed structured from the xml response
        """

        return handle_response(
            self.get_or_create_session().post(BASE_URL, params=payload, timeout=self.timeout))

    def close(self) -> None:
        """
        Closes the session and logout from the api
        """

        log.info("Closing session to securitas server")
        try:
            response = self.get({"Country": self.country,
                                 "user": self.username,
                                 "lang": self.lang,
                                 "request": "CLS",
                                 "hash": self.login_hash,
                                 "ID": self.generate_request_id()})

            result, login_hash = get_response_value(response)
            if result != "OK":
                log.error("Unable to close session: %s", json.dumps(response))

                raise ConnectionException("Unable to logout")
        finally:
            if self.session:
                try:
                    self.session.close()
                    self.session = None
                except:
                    pass

    def __exit__(self, *args):
        """
        Enable closing a session when used on context manager
        """

        self.close()

    def __enter__(self):
        """
        Enable connecting when used on context manager
        """

        self.connect()


class ConnectionException(IOError):
    """
    Exception when unable to connect
    """

    def __init__(self, *args):
        super(ConnectionException, self).__init__(*args)
