# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/session.py: Classes for managing zugbruecke sessions

    Required to run on platform / side: [UNIX]

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

import atexit
from ctypes import (
    _FUNCFLAG_CDECL,
    _FUNCFLAG_USE_ERRNO,
    _FUNCFLAG_USE_LASTERROR,
    DEFAULT_MODE,
)
import signal
import time
from types import FrameType
from typing import Any, Optional, Type

from .abc import DataABC, SessionClientABC
from .const import _FUNCFLAG_STDCALL, CONVENTIONS
from .config import Config
from .data import Data
from .definitions import DefinitionFunc
from .dll_client import DllClient
from .interpreter import Interpreter
from .lib import get_free_port, get_hash_of_string
from .log import Log
from .rpc import RpcClient, RpcServer
from .typeguard import typechecked
from .wenv import Env


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class SessionClient(SessionClientABC):
    """
    Managing a zugbruecke session
    """

    def __init__(self, config: Optional[Config] = None):

        self._p = Config() if config is None else config
        self._id = self._p["id"]
        self._dlls = {}  # loaded dlls
        self._client_up = True
        self._server_up = False

        # Store current working directory
        # self.dir_cwd = os.getcwd()

        # Start RPC server for callback routines
        self._p["port_socket_unix"] = get_free_port()
        self._rpc_server = RpcServer(
            ("localhost", self._p["port_socket_unix"]), "zugbruecke_unix"
        )  # Log is added later
        self._rpc_server.register_function(self.set_server_status, "set_server_status")
        self._rpc_server.server_forever_in_thread()

        # Start session logging
        self._log = Log(self._id, self._p, rpc_server=self._rpc_server)

        self._log.info("[session-client] STARTING ...")
        self._log.info(f'[session-client] Configured Wine-Python version is {str(self._p["pythonversion"]):s} for {self._p["arch"]:s}.')
        self._log.info(f'[session-client] Log socket port: {self._p["port_socket_unix"]:d}.')

        # Set data cache and parser
        self._data = Data(
            self._log, is_server=False, callback_server=self._rpc_server
        )

        # Register session destructur
        atexit.register(self.terminate)
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

        # Ensure a working Wine-Python environment
        env = Env(**self._p.export_dict())
        env.ensure()
        env.setup_zugbruecke()

        # Initialize interpreter session
        self._interpreter = Interpreter(self._id, self._p, self._log)

        # Wait for server to appear
        self._wait_for_server_status_change(target_status=True)

        # Fire up RPC client
        self._rpc_client = RpcClient.from_safe_connect(
            socket_path=("localhost", self._p["port_socket_wine"]),
            authkey="zugbruecke_wine",
            timeout_after_seconds=self._p["timeout_start"],
        )

        for name in (
            "FormatError",
            "get_last_error",
            "GetLastError",
            "set_last_error",
            "WinError",
            "find_msvcrt",
            "find_library",
            "path_unix_to_wine",
            "path_wine_to_unix",
        ):
            setattr(self, name, getattr(self._rpc_client, name))

        for name in ("load_library", "set_parameter", "terminate"):
            setattr(
                self,
                f"_{name:s}_on_server",
                getattr(self._rpc_client, name),
            )

        self._log.info("[session-client] STARTED.")

    def CFUNCTYPE(self, restype: Any, *argtypes: Any, use_errno: bool = False, use_last_error: bool = False) -> Type:

        flags = _FUNCFLAG_CDECL
        if use_errno:
            flags |= _FUNCFLAG_USE_ERRNO
        if use_last_error:
            flags |= _FUNCFLAG_USE_LASTERROR

        return DefinitionFunc.generate_callback_decorator(
            cache = self._data.cache,
            func_flags = flags,
            restype = restype,
            argtypes = list(argtypes),
        )

    def WINFUNCTYPE(self, restype: Any, *argtypes: Any, use_errno: bool = False, use_last_error: bool = False) -> Type:

        flags = _FUNCFLAG_STDCALL

        if use_errno:
            flags |= _FUNCFLAG_USE_ERRNO
        if use_last_error:
            flags |= _FUNCFLAG_USE_LASTERROR

        return DefinitionFunc.generate_callback_decorator(
            cache = self._data.cache,
            func_flags = flags,
            restype = restype,
            argtypes = list(argtypes),
        )

    def load_library(
        self,
        name: str,
        convention: str,
        mode: int = DEFAULT_MODE,
        use_errno: bool = False,
        use_last_error: bool = False,
    ):

        if convention not in CONVENTIONS:
            raise ValueError("unknown convention")

        if name in self._dlls.keys():
            return self._dlls[name]

        self._log.info(f'[session-client] Attaching to DLL file "{name:s}" with calling convention "{convention:s}" ...')

        hash_id = get_hash_of_string(name)

        try:
            self._load_library_on_server(
                name,
                hash_id,
                convention,
                mode,
                use_errno,
                use_last_error,
            )
        except OSError as e:
            self._log.error("[session-client] ... failed!")
            raise e

        self._dlls[name] = DllClient(
            name,
            hash_id,
            convention,
            self._log,
            self._rpc_client,
            self._data,
        )

        self._log.info("[session-client] ... attached.")

        return self._dlls[name]

    def get_parameter(self, key: str) -> Any:

        return self._p[key]

    def set_parameter(self, key: str, value: Any):

        if key == "id":
            raise ValueError("session id can not be changed")

        self._p[key] = value
        self._set_parameter_on_server(key, value)

    def set_server_status(self, status: bool):
        """
        Called by session server
        """

        self._server_up = status

    def terminate(
        self,
        signum: Optional[int] = None,  # Only required for for signal handling.
        frame: Optional[FrameType] = None,  # Only required for for signal handling.
    ):

        if not self._client_up:
            return

        self._log.info("[session-client] TERMINATING ...")

        try:
            self._terminate_on_server()
        except EOFError:  # EOFError is raised if server socket is closed - ignore it
            self._log.info("[session-client] Remote socket closed.")

        self._wait_for_server_status_change(
            target_status=False
        )  # Wait for server to appear

        self._interpreter.terminate()
        self._rpc_server.terminate()

        self._log.info("[session-client] TERMINATED.")
        self._log.terminate()

        self._client_up = False

    @property
    def config(self) -> Config:

        return self._p

    @property
    def id(self) -> str:

        return self._id

    @property
    def client_up(self) -> bool:

        return self._client_up

    @property
    def server_up(self) -> bool:

        return self._server_up

    @property
    def data(self) -> DataABC:  # Accessed by CtypesSession

        return self._data

    def _wait_for_server_status_change(self, target_status: bool):

        # Does the status have to change?
        if target_status == self._server_up:

            # No, so get out of here
            return

        self._log.info(f'[session-client] Waiting for session-server to be {"up" if target_status else "down":s} ...')

        # Timeout
        timeout_after_seconds = self._p[
            "timeout_start" if target_status else "timeout_stop"
        ]
        # Already waited for ...
        started_waiting_at = time.time()

        # Run loop until socket appears
        while target_status != self._server_up:

            # Wait before trying again
            time.sleep(0.01)

            # Time out
            if time.time() >= (started_waiting_at + timeout_after_seconds):
                break

        # Handle timeout
        if target_status != self._server_up:

            self._log.info(f"[session-client] ... wait timed out (after {time.time() - started_waiting_at:0.2f} seconds).")

            if target_status:
                raise TimeoutError("session server did not appear")
            else:
                raise TimeoutError("session server could not be stopped")

        self._log.info(f'[session-client] ... session server is {"up" if target_status else "down":s} (after {time.time() - started_waiting_at:0.2f} seconds).')
