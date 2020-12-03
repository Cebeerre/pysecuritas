# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""

from typing import Dict, List

DALARM_OPS: Dict[str, str] = {
    'ARM': 'arm all sensors (inside)',
    'ARMDAY': 'arm in day mode (inside)',
    'ARMNIGHT': 'arm in night mode (inside)',
    'PERI': 'arm (only) the perimeter sensors',
    'DARM': 'disarm everything (not the annex)',
    'ARMANNEX': 'arm the secondary alarm',
    'DARMANNEX': 'disarm the secondary alarm',
    'EST': 'return the panel status',
    'IMG': 'Take a picture (requires -s)'
}

DAPI_OPS: Dict[str, str] = {
    'ACT_V2': 'get the activity log',
    'SRV': 'SIM Number and INSTIBS',
    'MYINSTALLATION': 'Sensor IDs and other info'
}

ALARM_OPS: List[str] = list(DALARM_OPS.keys())
API_OPS: List[str] = list(DAPI_OPS.keys())


def get_available_commands() -> Dict[str, str]:
    """
    Returns a dictionary with all available commands and their descriptions

    :return: a dictionary with all available commands
    """

    commands: Dict[str, str] = DALARM_OPS.copy()
    commands.update(DAPI_OPS)

    return commands
