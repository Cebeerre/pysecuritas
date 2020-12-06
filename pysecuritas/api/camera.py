# -*- coding: utf-8 -*-
"""
    :copyright: © pysecuritas, All Rights Reserved
"""
import base64
from datetime import datetime
from typing import Dict

from pysecuritas.api.installation import DEFAULT_TIMEOUT
from pysecuritas.api.installation import Installation

ID_SERVICE = 1


def get_available_commands() -> Dict:
    """
    Returns all available commands
    """

    return {
        "IMG": "Take a picture (requires -s)"
    }


class Camera(Installation):
    """
    The entrypoint to retrieve images from cameras
    """

    def __init__(self, session, timeout=DEFAULT_TIMEOUT):
        """
        Initializes alarm api
        """

        super(Camera, self).__init__(session, timeout)
        self.instibs = None

    def execute_command(self, command) -> Dict:
        """
        Executes a command

        :param command command to be executed

        :return: the result from the operation
        """

        if command == "IMG":
            return self.capture_snapshots()

    def capture_snapshots(self) -> Dict:
        """
        Captures snapshots from a camera
        """

        installation = Installation(self.session)
        if self.instibs is None:
            self.instibs = installation.get_sim_and_instibs()["INSTALATION"]["INSTIBS"]

        self.async_request("IMG", device=self.session.sensor, instibs=self.instibs, idservice=ID_SERVICE)
        images = self.get_inf()["DEVICES"]["DEVICE"]["IMG"]
        files = {}
        i = 0
        for img in images:
            i += 1
            filename = datetime.now().strftime('%Y%m%d%H%M%S') + '_' + str(i) + '.jpg'
            files.update({"IMG" + str(i): filename})
            with open(filename, "wb") as f:
                f.write(base64.b64decode(img['#text']))

        return {"RES": "OK", "MSG": "Images written to disk.", "FILES": files}
