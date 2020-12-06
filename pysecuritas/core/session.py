# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

import json
import logging
from datetime import datetime
from typing import Dict

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from pysecuritas.core.utils import handle_response

log = logging.getLogger("pysecuritas")

# in seconds
DEFAULT_TIMEOUT = 30
BASE_URL = "https://mob2217.securitasdirect.es:12010/WebService/ws.do"


class Session:
    """
    A session will handle connectivity to interact with securitas installation and devices
    """

    def __init__(self, username, password, installation, country, lang, sensor=None):
        """
        Session initializer
        """

        self.username = username
        self.password = password
        self.installation = installation
        self.country = country.upper()
        self.lang = lang.lower()
        self.sensor = sensor
        self.timeout = DEFAULT_TIMEOUT
        self.session = None
        self.login_hash = None
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'

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

    def build_payload(self, **params):
        """
        Builds a payload with session parameters and custom parameters
        """

        payload = {"Country": self.country, "user": self.username,
                   "pwd": self.password, "lang": self.lang, "hash": self.login_hash, "callby": "AND_61",
                   "numinst": self.installation, "panel": "SDVFAST"}
        payload.update(params)

        return payload

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

        login_hash = response.get("HASH")
        if response.get("RES") != "OK" or not login_hash:
            log.error("Unable to login: %s", json.dumps(response))

            raise ConnectionException("Unable to login ")

        log.info("Connected to securitas server")
        self.login_hash = login_hash

    def is_connected(self) -> bool:
        """
        Check if this session is connected
        """

        return self.login_hash is not None

    def validate_connection(self) -> None:
        """
        Check if session is already connected, if not, raise an exception
        """

        if not self.is_connected():
            raise ConnectionException("Session is not connected ")

    def get(self, payload) -> Dict:
        """
        Performs a GET request and returns a dictionary with the parsed response
        If response happens to end in error, session will try to re-login and repeat the request
        :param payload get request parameters

        :return: a parsed structured from the xml response
        """

        def _get():
            return handle_response(self.get_or_create_session().get(BASE_URL, params=payload, timeout=self.timeout))

        result = _get()
        if result.get("ERR") in ("60067", "60022"):
            self.session = None
            self.connect()
            payload["hash"] = self.login_hash

            return _get()

        return result

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

            if response.get("RES") != "OK":
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

        return self


class ConnectionException(Exception):
    """
    Exception when unable to connect
    """

    def __init__(self, *args):
        super(ConnectionException, self).__init__(*args)
