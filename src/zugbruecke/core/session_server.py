# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/session_server.py: Handling session on Wine side

    Required to run on platform / side: [WINE]

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

import ctypes
import ctypes.util
import traceback
from typing import Any

from .data import data_class
from .dll_server import DllServer
from .log import Log
from .path import PathStyles
from .rpc import mp_client_safe_connect, mp_server_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class session_server_class:
    def __init__(self, session_id, parameter):

        # Store session id and parameter
        self.id = session_id
        self.p = parameter

        # Connect to Unix side
        self.rpc_client = mp_client_safe_connect(
            socket_path=("localhost", self.p["port_socket_unix"]),
            authkey="zugbruecke_unix",
            timeout_after_seconds=self.p["timeout_start"],
        )

        # Start logging session and connect it with log on unix side
        self.log = Log(self.id, self.p, rpc_client=self.rpc_client)

        # Status log
        self.log.out("[session-server] STARTING ...")

        # Mark session as up
        self.up = True

        # Offer methods for converting paths
        path = PathStyles()
        self.path_unix_to_wine = path.unix_to_wine
        self.path_wine_to_unix = path.wine_to_unix

        # Start dict for dll files and routines
        self.dll_dict = {}

        # Organize all DLL types
        self._conventions = {
            "cdll": ctypes.CDLL,
            "windll": ctypes.WinDLL,
            "oledll": ctypes.OleDLL,
        }

        # Set data cache and parser
        self.data = data_class(
            self.log, is_server=True, callback_client=self.rpc_client
        )

        # Create server
        self.rpc_server = mp_server_class(
            ("localhost", self.p["port_socket_wine"]),
            "zugbruecke_wine",
            log=self.log,
            terminate_function=self.__terminate__,
        )

        # Register call: Accessing a dll
        self.rpc_server.register_function(self._load_library, "load_library")
        # Expose routine for updating parameters
        self.rpc_server.register_function(self.__set_parameter__, "set_parameter")
        # Register destructur: Call goes into xmlrpc-server first, which then terminates parent
        self.rpc_server.register_function(self.rpc_server.terminate, "terminate")
        # Convert path: Unix to Wine
        self.rpc_server.register_function(self.path_unix_to_wine, "path_unix_to_wine")
        # Convert path: Wine to Unix
        self.rpc_server.register_function(self.path_wine_to_unix, "path_wine_to_unix")

        # Expose ctypes stuff
        self.__expose_ctypes_routines__()

        # Status log
        self.log.out(
            "[session-server] ctypes server is listening on port %d."
            % self.p["port_socket_wine"]
        )
        self.log.out("[session-server] STARTED.")
        self.log.out("[session-server] Serve forever ...")

        # Run server ...
        self.rpc_server.server_forever_in_thread(daemon=False)

        # Indicate to session client that the server is up
        self.rpc_client.set_server_status(True)

    def __expose_ctypes_routines__(self):

        # As-is exported platform-specific routines from ctypes
        for mod, routine in [
            (ctypes, "FormatError"),
            (ctypes, "get_last_error"),
            (ctypes, "GetLastError"),
            (ctypes, "WinError"),
            (ctypes, "set_last_error"),
            (ctypes.util, "find_msvcrt"),
            (ctypes.util, "find_library"),
        ]:

            self.rpc_server.register_function(
                getattr(mod, routine), "ctypes_" + routine
            )

    def _load_library(
        self,
        name: str,
        hash_id: str,
        convention: str,
        mode: int,
        use_errno: bool,
        use_last_error: bool,
    ):
        """
        Exposed interface, called by session client
        """

        if name in self.dll_dict.keys():
            return

        self.log.out(
            '[session-server] Attaching to DLL file "{FN:s}" with calling convention "{CONVENTION:s}" ...'.format(
                FN=name,
                CONVENTION=convention,
            )
        )

        try:
            handler = self._conventions[convention](
                name,
                mode=mode,
                handle=None,
                use_errno=use_errno,
                use_last_error=use_last_error,
            )
        except OSError as e:
            self.log.out("[session-server] ... failed!")
            raise e
        except Exception as e:
            self.log.err(traceback.format_exc())
            raise e

        self.dll_dict[name] = DllServer(
            name,
            hash_id,
            convention,
            handler,
            self.log,
            self.rpc_server,
            self.data,
        )

        self.log.out("[session-server] ... attached.")

    def __set_parameter__(self, key: str, value: Any):

        self.p[key] = value

    def __terminate__(self):
        """
        Exposed interface
        """

        # Run only if session still up
        if not self.up:
            return

        # Status log
        self.log.out("[session-server] TERMINATING ...")

        # Terminate log
        self.log.terminate()

        # Session down
        self.up = False

        # Status log
        self.log.out("[session-server] TERMINATED.")

        # Indicate to session client that server was terminated
        self.rpc_client.set_server_status(False)
