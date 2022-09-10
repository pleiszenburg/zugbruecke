# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/log.py: Classes for gathering, managing & displaying logs

    Required to run on platform / side: [UNIX, WINE]

    Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
from typing import Any, List, Union

from .abc import ConfigABC, LogABC, MessageABC, RpcClientABC, RpcServerABC
from .const import PLATFORMS
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
    Gathering, managing & displaying logs
    """

    def __init__(
        self,
        session_id: str,
        parameter: ConfigABC,
        rpc_server: Union[None, RpcServerABC] = None,
        rpc_client: Union[None, RpcClientABC] = None,
    ):

        self._id = session_id
        self._p = parameter

        self._up = True

        self._f = None
        if self._p["log_write"]:
            self._f = "zb_{ID:s}_{PLATFORM:s}.txt".format(
                ID=self._id,
                PLATFORM=self._p["platform"],
            )

        if rpc_server is not None:
            rpc_server.register_function(self._receive, "transfer_message")
        self._transfer_message = (
            rpc_client.transfer_message if rpc_client is not None else None
        )

    def err(self, *raw_messages: Any, level: int = 1):

        if level <= self._p["log_level"]:
            self._process_raw(*raw_messages, pipe="err", level=level)

    def out(self, *raw_messages: Any, level: int = 1):

        if level <= self._p["log_level"]:
            self._process_raw(*raw_messages, pipe="out", level=level)

    def terminate(self):

        if not self._up:
            return

        self._up = False

    def _process_raw(self, *raw_messages: Any, pipe: str, level: int):

        for raw_message in raw_messages:
            for message in Message.from_raw(
                raw_message, pipe, level, self._id, self._p["platform"]
            ):
                self._process(message)

    def _process(self, message: MessageABC):

        if self._p["std" + message.pipe]:
            message.print()

        if self._transfer_message is not None:
            self._send(message)

        if self._p["log_write"]:
            message.store(self._f)

    def _send(self, message: MessageABC):

        self._transfer_message(message.as_serialized())

    def _receive(self, serialized_message: str):

        self._process(Message.from_serialized(serialized_message))


@typechecked
class Message(MessageABC):
    """
    Container for log messages
    """

    def __init__(
        self,
        level: int,
        platform: str,
        id: str,
        time: float,
        pipe: str,
        cnt: str,
    ):

        assert platform in PLATFORMS
        assert pipe in ("out", "err")

        self._level, self._platform, self._id, self._time, self._pipe, self._cnt = (
            level,
            platform,
            id,
            time,
            pipe,
            cnt,
        )

    def as_serialized(self) -> str:

        return json.dumps(
            dict(
                level=self._level,
                platform=self._platform,
                id=self._id,
                time=self._time,
                pipe=self._pipe,
                cnt=self._cnt,
            )
        )

    def print(self):

        message_list = []

        message_list.append(
            c["GREY"] + "(%.2f/%s) " % (self._time, self._id) + c["RESET"]
        )

        message_list.append(c["BLUE"] if self._platform == "UNIX" else c["MAGENTA"])
        message_list.append("%s " % self._platform + c["RESET"])

        message_list.append(c["GREEN"] if self._pipe == "out" else c["RED"])
        message_list.append(self._pipe[0] + c["RESET"] + ": ")
        if any(
            ext in self._cnt
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
        message_list.append(self._cnt + c["RESET"] + "\n")

        message_string = "".join(message_list)

        pipe = sys.stdout if self._pipe == "out" else sys.stderr
        pipe.write(message_string)

    def store(self, fn):

        with open(fn, "a+") as f:
            f.write(self.as_serialized() + "\n")

    @property
    def pipe(self) -> str:

        return self._pipe

    @classmethod
    def from_raw(
        cls, raw_message: Any, pipe: str, level: int, id: str, platform: str
    ) -> List[MessageABC]:

        raw_message = (
            raw_message if isinstance(raw_message, str) else pformat(raw_message)
        )
        message_time = round(time.time(), 2)
        return [
            cls(
                level=level,
                platform=platform,
                id=id,
                time=message_time,
                pipe=pipe,
                cnt=line,
            )
            for line in raw_message.split("\n")
            if len(line.strip()) != 0
        ]

    @classmethod
    def from_serialized(cls, serialized: str) -> MessageABC:

        return cls(**json.loads(serialized))
