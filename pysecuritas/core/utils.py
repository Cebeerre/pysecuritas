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

    return clean_response(xmltodict.parse(response.text))


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
