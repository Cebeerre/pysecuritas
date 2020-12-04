# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""
from typing import Dict

import xmltodict


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


def clean_response(result) -> Dict:
    """
    Clean a response by removing unnecessary fields
    """

    result = result["PET"]
    try:
        del result["BLOQ"]
    except (KeyError, TypeError):
        pass

    return result
