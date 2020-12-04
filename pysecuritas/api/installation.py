# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""
import time
from typing import Dict

from pysecuritas.core.utils import clean_response, get_response_value

DEFAULT_TIMEOUT = 60
RATE_LIMIT = 1
TIME_FILTER = "3"
ACTIVITY_FILTER = "0"


def get_available_commands() -> Dict:
    """
    Returns all available commands
    """

    return {
        "ACT_V2": "get the activity log",
        "SRV": "SIM Number and INSTIBS",
        "MYINSTALLATION": "Sensor IDs and other info"
    }


def handle_result(status, result):
    """
    Handle different status of an async request

    :param status current status
    :param result current result

    :return: the cleaned result if it's ok, if waiting, returns None
    """

    if status == "WAIT":
        return

    if status == "ERROR":
        raise RequestException(result["PET"]["MSG"])

    if status == "OK":
        return clean_response(result)


class Installation:
    """
    The entrypoint to perform any action on an alarm such as arm and disarm
    """

    def __init__(self, session, timeout=DEFAULT_TIMEOUT):
        """
        Initializes endpoint api with a session

        :param session session to access securitas api
        :param timeout timeout before given up on a request attempt
        """

        self.session = session
        self.timeout = timeout

    def execute_command(self, command) -> Dict:
        """
        Executes a command

        :param command command to be executed

        :return: the result from the operation
        """

        if command == "ACT_V2":
            return self.get_activity_log()

        if command == "SRV":
            return self.get_sim_and_instibs()

        if command == "MYINSTALLATION":
            return self.get_installation_info()

    def get_activity_log(self, request_id=None) -> Dict:
        """
        Gets activity log

        :param request_id request id already calculated (reused)
        """

        return self.request("ACT_V2", request_id, timefilter=TIME_FILTER, activityfilter=ACTIVITY_FILTER)

    def get_sim_and_instibs(self) -> Dict:
        """
        Gets information about SIM number and INSTIBS
        """

        return self.request("SRV")

    def get_installation_info(self) -> Dict:
        """
        Gets generic information about the installation including sensor IDs
        """

        return self.request("MYINSTALLATION")

    def get_inf(self) -> Dict:
        """
        Waits for signal 16 and gets the result from INF command

        :return: a response or nothing if timeout happens
        """

        request_id = self.session.generate_request_id()
        self.session.validate_connection()
        threshold = time.time() + self.timeout
        while time.time() < threshold:
            time.sleep(RATE_LIMIT)
            log = self.get_activity_log(request_id)["LIST"]["REG"][0]
            if log["@signaltype"] == "16":
                time.sleep(RATE_LIMIT)
                return self.request("INF", request_id, idsignal=log["@idsignal"], signaltype="16")

    def async_request(self, action, **params) -> Dict:
        """
        Performs a double request
        The first request is sent asynchronously with a given id
        That same id is then used to get the result

        :param action action to be performed
        :param params additional parameters for the request

        :return: a response or nothing if timeout happens
        """

        payload = self.session.build_payload(request=action, ID=self.session.generate_request_id(), **params)
        self.session.validate_connection()
        payload["request"] = action + "1"
        self.session.get(payload)
        time.sleep(RATE_LIMIT)
        payload["request"] = action + "2"
        threshold = time.time() + self.timeout
        while time.time() < threshold:
            time.sleep(RATE_LIMIT)
            result = self.session.get(payload)
            result = handle_result(get_response_value(result)[0], result)
            if result:
                return result

    def request(self, action, request_id=None, **params) -> Dict:
        """
        Performs a simple request

        :param action action to be performed
        :param params additional parameters for the request
        :param request_id request id already calculated (reused)

        :return: a response or nothing if timeout happens
        """

        payload = self.session.build_payload(request=action,
                                             ID=request_id if request_id else self.session.generate_request_id(),
                                             **params)
        self.session.validate_connection()
        result = self.session.get(payload)
        result = handle_result(get_response_value(result)[0], result)
        if result:
            return result


class RequestException(Exception):
    """
    Exception when unable to perform an action
    """

    def __init__(self, *args):
        super(RequestException, self).__init__(*args)
