# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/log.py: Classes for gathering, managing & displaying logs

    Required to run on platform / side: [UNIX, WINE]

    Copyright (C) 2017-2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import json
from pprint import pformat
import sys
import time
from typing import Any, Dict, List, Union

from .abc import LogABC, RpcClientABC, RpcServerABC
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONSTANTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://en.wikipedia.org/wiki/ANSI_escape_code
c = {
    "RESET": "\033[0;0m",
    "BOLD": "\033[;1m",
    "REVERSE": "\033[;7m",
    "GREY": "\033[1;30m",
    "RED": "\033[1;31m",
    "GREEN": "\033[1;32m",
    "YELLOW": "\033[1;33m",
    "BLUE": "\033[1;34m",
    "MAGENTA": "\033[1;35m",
    "CYAN": "\033[1;36m",
    "WHITE": "\033[1;37m",
}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LOG CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Log(LogABC):
    """
    gathering, managing & displaying logs
    """

    def __init__(
        self,
        session_id: str,
        parameter: Dict,
        rpc_server: Union[None, RpcServerABC] = None,
        rpc_client: Union[None, RpcClientABC] = None,
    ):

        # Store id and parameter
        self._id = session_id
        self._p = parameter

        # Determine platform
        if "platform" not in self._p.keys():
            self._p["platform"] = "UNIX"

        # Create filenames for logfiles
        self._f = None
        if self._p["log_write"]:
            self._f = {
                "out": "zb_{ID:s}_{PLATFORM:s}_out.txt".format(
                    ID=self._id,
                    PLATFORM=self._p["platform"],
                ),
                "err": "zb_{ID:s}_{PLATFORM:s}_err.txt".format(
                    ID=self._id,
                    PLATFORM=self._p["platform"],
                ),
            }

        # Setup RPC server
        self._server = rpc_server
        if rpc_server is not None:
            self._server.register_function(self._receive_message, "transfer_message")

        # Setup RPC client
        self._client = rpc_client

        # Log is up
        self._up = True

    def err(self, *raw_messages: Any, level: int = 1):

        if level <= self._p["log_level"]:
            self._process_raw_messages(raw_messages, "err", level)

    def out(self, *raw_messages: Any, level: int = 1):

        if level <= self._p["log_level"]:
            self._process_raw_messages(raw_messages, "out", level)

    def terminate(self):

        if not self._up:
            return

        self._up = False

    def _print_message(self, message: Dict):

        message_list = []

        message_list.append(
            c["GREY"] + "(%.2f/%s) " % (message["time"], message["id"]) + c["RESET"]
        )
        if message["platform"] == "UNIX":
            message_list.append(c["BLUE"])
        elif message["platform"] == "WINE":
            message_list.append(c["MAGENTA"])
        else:
            message_list.append(c["WHITE"])
        message_list.append("%s " % message["platform"] + c["RESET"])
        if message["pipe"] == "out":
            message_list.append(c["GREEN"])
        elif message["pipe"] == "err":
            message_list.append(c["RED"])
        message_list.append(message["pipe"][0] + c["RESET"])
        message_list.append(": ")
        if any(
            ext in message["cnt"]
            for ext in [
                "fixme:",
                "err:",
                "wine: ",
                "wine client error",
                ":warn:",
                ":trace:",
            ]
        ):
            message_list.append(c["GREY"])
        else:
            message_list.append(c["WHITE"])
        message_list.append(message["cnt"] + c["RESET"])
        message_list.append("\n")

        message_string = "".join(message_list)

        if message["pipe"] == "out":
            sys.stdout.write(message_string)
        elif message["pipe"] == "err":
            sys.stderr.write(message_string)
        else:
            raise ValueError("unknown pipe name")

    def _process_raw_messages(self, raw_messages: Any, pipe: str, level: int):

        for raw_message in raw_messages:
            for message in self._compile_raw_message(raw_message, pipe, level):
                self._process_message(message)

    def _compile_raw_message(
        self, raw_message: Any, pipe: str, level: int
    ) -> List[Dict]:

        raw_message = (
            raw_message if isinstance(raw_message, str) else pformat(raw_message)
        )
        message_time = round(time.time(), 2)
        return [
            {
                "level": level,
                "platform": self._p["platform"],
                "id": self._id,
                "time": message_time,
                "pipe": pipe,
                "cnt": line,
            }
            for line in raw_message.split("\n")
            if len(line.strip()) != 0
        ]

    def _process_message(self, mesage: Dict):

        if self._p["std" + mesage["pipe"]]:
            self._print_message(mesage)

        if self._client is not None:
            self._send_message(mesage)

        if self._p["log_write"]:
            self._store_message(mesage)

    def _send_message(self, message: Dict):

        self._client.transfer_message(json.dumps(message))

    def _receive_message(self, serialized_message: str):

        self._process_message(json.loads(serialized_message))

    def _store_message(self, message: Dict):

        with open(self._f[message["pipe"]], "a+") as f:
            f.write(json.dumps(message) + "\n")
