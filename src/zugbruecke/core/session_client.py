# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/session.py: Classes for managing zugbruecke sessions

    Required to run on platform / side: [UNIX]

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

import atexit
from ctypes import (
    _FUNCFLAG_CDECL,
    _FUNCFLAG_USE_ERRNO,
    _FUNCFLAG_USE_LASTERROR,
    DEFAULT_MODE,
)
import signal
import time
from typing import Union

from .abc import ConfigABC, DataABC, SessionClientABC
from .const import _FUNCFLAG_STDCALL, CONVENTIONS
from .config import Config
from .data import data_class
from .dll_client import DllClient
from .interpreter import Interpreter
from .lib import get_free_port, get_hash_of_string
from .log import Log
from .rpc import mp_client_safe_connect, mp_server_class
from .wenv import Env


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class SessionClient(SessionClientABC):
    """
    Managing a zugbruecke session
    """

    def __init__(self, config: Union[ConfigABC, None] = None):

        self._p = Config() if config is None else config
        self._id = self._p["id"]
        self._dlls = {}  # loaded dlls
        self._client_up = True
        self._server_up = False

        # Store current working directory
        # self.dir_cwd = os.getcwd()

        # Start RPC server for callback routines
        self._p["port_socket_unix"] = get_free_port()
        self._rpc_server = mp_server_class(
            ("localhost", self._p["port_socket_unix"]), "zugbruecke_unix"
        )  # Log is added later
        self._rpc_server.register_function(
            self._set_server_status, "set_server_status"
        )
        self._rpc_server.server_forever_in_thread()

        # Start session logging
        self._log = Log(self._id, self._p, rpc_server=self._rpc_server)

        self._log.out("[session-client] STARTING ...")
        self._log.out(
            "[session-client] Configured Wine-Python version is {PYTHONVERSION:s} for {ARCH:s}.".format(
                PYTHONVERSION = self._p["pythonversion"], ARCH = self._p["arch"],
            )
        )
        self._log.out(
            "[session-client] Log socket port: {PORT:d}.".format(PORT = self._p["port_socket_unix"])
        )

        # Set data cache and parser
        self._data = data_class(
            self._log, is_server=False, callback_server=self._rpc_server
        )

        # Register session destructur
        atexit.register(self.terminate)
        signal.signal(signal.SIGINT, self.terminate)
        signal.signal(signal.SIGTERM, self.terminate)

        # Ensure a working Wine-Python environment
        env = Env(**self._p.as_dict())
        env.ensure()
        env.setup_zugbruecke()

        # Initialize interpreter session
        self._interpreter = Interpreter(self._id, self._p, self._log)

        # Wait for server to appear
        self._wait_for_server_status_change(target_status=True)

        # Fire up xmlrpc client
        self._rpc_client = mp_client_safe_connect(
            socket_path=("localhost", self._p["port_socket_wine"]),
            authkey="zugbruecke_wine",
            timeout_after_seconds=self._p["timeout_start"],
        )

        for routine in (
            "FormatError",
            "get_last_error",
            "GetLastError",
            "set_last_error",
            "WinError",
            "find_msvcrt",
            "find_library",
        ):
            name = "ctypes_{ROUTINE:s}".format(ROUTINE = routine)
            setattr(self, name, getattr(self._rpc_client, name))

        self._log.out("[session-client] STARTED.")

    def ctypes_CFUNCTYPE(self, restype, *argtypes, **kw):

        flags = _FUNCFLAG_CDECL

        if kw.pop("use_errno", False):
            flags |= _FUNCFLAG_USE_ERRNO
        if kw.pop("use_last_error", False):
            flags |= _FUNCFLAG_USE_LASTERROR
        if kw:
            raise ValueError("unexpected keyword argument(s) %s" % kw.keys())

        return self._data.generate_callback_decorator(flags, restype, *argtypes)

    def ctypes_WINFUNCTYPE(self, restype, *argtypes, **kw):  # EXPORT

        flags = _FUNCFLAG_STDCALL

        if kw.pop("use_errno", False):
            flags |= _FUNCFLAG_USE_ERRNO
        if kw.pop("use_last_error", False):
            flags |= _FUNCFLAG_USE_LASTERROR
        if kw:
            raise ValueError("unexpected keyword argument(s) %s" % kw.keys())

        return self._data.generate_callback_decorator(flags, restype, *argtypes)

    def load_library(
        self,
        name: str,
        convention: str,
        mode: int = DEFAULT_MODE,
        use_errno: bool = False,
        use_last_error: bool = False,
    ):
        """
        Public API
        """

        if convention not in CONVENTIONS:
            raise ValueError("unknown convention")

        if name in self._dlls.keys():
            return self._dlls[name]

        self._log.out(
            '[session-client] Attaching to DLL file "{FN:s}" with calling convention "{CONVENTION:s}" ...'.format(
                FN=name,
                CONVENTION=convention,
            )
        )

        hash_id = get_hash_of_string(name)

        try:
            self._rpc_client.load_library(
                name,
                hash_id,
                convention,
                mode,
                use_errno,
                use_last_error,
            )
        except OSError as e:
            self._log.out("[session-client] ... failed!")
            raise e

        self._dlls[name] = DllClient(
            name,
            hash_id,
            convention,
            self._log,
            self._rpc_client,
            self._data,
        )

        self._log.out("[session-client] ... attached.")

        return self._dlls[name]

    def path_unix_to_wine(self, in_path):

        if not isinstance(in_path, str):
            raise TypeError("in_path must by of type str")

        return self._rpc_client.path_unix_to_wine(in_path)

    def path_wine_to_unix(self, in_path):

        if not isinstance(in_path, str):
            raise TypeError("in_path must by of type str")

        return self._rpc_client.path_wine_to_unix(in_path)

    def get_parameter(self, key):

        return self._p[key]

    def set_parameter(self, key, value):

        self._p[key] = value

        self._rpc_client.set_parameter({key: value})

    def terminate(self, signum=None, frame=None):

        # Run only if session is still up
        if not self._client_up:
            return

        # Log status
        self._log.out("[session-client] TERMINATING ...")

        try:

            # Tell server via message to terminate
            self._rpc_client.terminate()

        except EOFError:

            # EOFError is raised if server socket is closed - ignore it
            self._log.out("[session-client] Remote socket closed.")

        # Wait for server to appear
        self._wait_for_server_status_change(target_status=False)

        # Destruct interpreter session
        self._interpreter.terminate()

        # Terminate callback server
        self._rpc_server.terminate()

        # Log status
        self._log.out("[session-client] TERMINATED.")

        # Terminate log
        self._log.terminate()

        # Session down
        self._client_up = False

    @property
    def data(self) -> DataABC:

        return self._data

    def _set_server_status(self, status):

        # Interface for session server through RPC
        self._server_up = status

    def _wait_for_server_status_change(self, target_status):

        # Does the status have to change?
        if target_status == self._server_up:

            # No, so get out of here
            return

        # Debug strings
        STATUS_DICT = {True: "up", False: "down"}
        # Config keys for timeouts
        CONFIG_DICT = {True: "timeout_start", False: "timeout_stop"}

        # Log status
        self._log.out(
            "[session-client] Waiting for session-server to be %s ..."
            % STATUS_DICT[target_status]
        )

        # Time-step
        wait_for_seconds = 0.01
        # Timeout
        timeout_after_seconds = self._p[CONFIG_DICT[target_status]]
        # Already waited for ...
        started_waiting_at = time.time()

        # Run loop until socket appears
        while target_status != self._server_up:

            # Wait before trying again
            time.sleep(wait_for_seconds)

            # Time out
            if time.time() >= (started_waiting_at + timeout_after_seconds):
                break

        # Handle timeout
        if target_status != self._server_up:

            # Log status
            self._log.out(
                "[session-client] ... wait timed out (after %0.2f seconds)."
                % (time.time() - started_waiting_at)
            )

            if target_status:
                raise TimeoutError("session server did not appear")
            else:
                raise TimeoutError("session server could not be stopped")

        # Log status
        self._log.out(
            "[session-client] ... session server is %s (after %0.2f seconds)."
            % (STATUS_DICT[target_status], time.time() - started_waiting_at)
        )
