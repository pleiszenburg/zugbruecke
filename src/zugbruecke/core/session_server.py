# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/session_server.py: Handling session on Wine side

    Required to run on platform / side: [WINE]

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

import ctypes
import ctypes.util
import traceback
from typing import Any

from .abc import ConfigABC, SessionServerABC
from .data import Data
from .dll_server import DllServer
from .log import Log
from .path import PathStyles
from .rpc import RpcClient, RpcServer
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WRAPPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CONVENTIONS = {
    "cdll": ctypes.CDLL,
    "windll": ctypes.WinDLL,
    "oledll": ctypes.OleDLL,
}


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class SessionServer(SessionServerABC):
    """
    Managing a zugbruecke session
    """

    def __init__(self, config: ConfigABC):

        self._p = config
        self._id = self._p["id"]
        self._up = True
        self._dlls = {}

        self._rpc_client = RpcClient.from_safe_connect(
            socket_path=("localhost", self._p["port_socket_unix"]),
            authkey="zugbruecke_unix",
            timeout_after_seconds=self._p["timeout_start"],
        )

        self._log = Log(self._id, self._p, rpc_client=self._rpc_client)
        self._log.info("[session-server] STARTING ...")

        self._data = Data(
            self._log, is_server=True, callback_client=self._rpc_client
        )

        path = PathStyles()
        self.path_unix_to_wine = path.unix_to_wine
        self.path_wine_to_unix = path.wine_to_unix

        self._rpc_server = RpcServer(
            ("localhost", self._p["port_socket_wine"]),
            "zugbruecke_wine",
            log=self._log,
            terminate_function=self._terminate,
        )

        for source, name in [
            (ctypes, "FormatError"),
            (ctypes, "get_last_error"),
            (ctypes, "GetLastError"),
            (ctypes, "WinError"),
            (ctypes, "set_last_error"),
            (ctypes.util, "find_msvcrt"),
            (ctypes.util, "find_library"),
            (self, "load_library"),
            (self, "set_parameter"),
            (self._rpc_server, "terminate"),
            (self, "path_unix_to_wine"),
            (self, "path_wine_to_unix"),
        ]:
            self._rpc_server.register_function(getattr(source, name), name)

        self._log.info(f'[session-server] ctypes server is listening on port {self._p["port_socket_wine"]:d}.')
        self._log.info("[session-server] STARTED.")
        self._log.info("[session-server] Serve forever ...")

        self._rpc_server.server_forever_in_thread(daemon=False)
        self._rpc_client.set_server_status(True)

    def load_library(
        self,
        name: str,
        hash_id: str,
        convention: str,
        mode: int,
        use_errno: bool,
        use_last_error: bool,
    ):
        """
        Called by session client
        """

        if name in self._dlls.keys():
            return

        self._log.info(f'[session-server] Attaching to DLL file "{name:s}" with calling convention "{convention:s}" ...')

        try:
            handler = CONVENTIONS[convention](
                name,
                mode=mode,
                handle=None,
                use_errno=use_errno,
                use_last_error=use_last_error,
            )
        except OSError as e:
            self._log.error("[session-server] ... failed!")
            raise e
        except Exception as e:
            self._log.error(traceback.format_exc())
            raise e

        self._dlls[name] = DllServer(
            name,
            hash_id,
            convention,
            handler,
            self._log,
            self._rpc_server,
            self._data,
        )

        self._log.info("[session-server] ... attached.")

    def set_parameter(self, key: str, value: Any):
        """
        Called by session client
        """

        self._p[key] = value

    def _terminate(self):
        """
        Called by session client via RPC server termination
        """

        if not self._up:
            return

        self._log.info("[session-server] TERMINATING ...")
        self._log.terminate()
        self._up = False
        self._log.info("[session-server] TERMINATED.")
        self._rpc_client.set_server_status(False)
