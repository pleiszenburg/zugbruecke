# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/dll_server.py: Classes for managing the access to DLLs

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

from ctypes import CDLL
import traceback
from typing import Union

from .abc import DataABC, DllServerABC, LogABC, RpcServerABC
from .routine_server import RoutineServer
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class DllServer(DllServerABC):
    """
    Representing one idividual dll to be called into
    """

    def __init__(
        self,
        name: str,
        hash_id: str,
        convention: str,
        handler: CDLL,
        log: LogABC,
        rpc_server: RpcServerABC,
        data: DataABC,
    ):

        self._name = name
        self._convention = convention
        self._hash_id = hash_id
        self._handler = handler

        self._log = log
        self._rpc_server = rpc_server
        self._data = data

        self._routines = {}

        for name in (
            "get_repr",
            "register_routine",
        ):
            self._rpc_server.register_function(
                getattr(self, name),
                f"{self._hash_id:s}_{name:s}",
            )

    def get_repr(self) -> str:
        """
        Called by DLL client
        """

        return repr(self._handler)

    def register_routine(self, name: Union[str, int]):
        """
        Called by DLL client
        """

        if name in self._routines.keys():
            return

        self._log.info(f'[dll-server] Trying to access "{str(name):s}" in DLL file "{self._name:s}" ...')

        try:
            if isinstance(name, str):
                routine_handler = getattr(self._handler, name)
            else:
                routine_handler = self._handler[name]
        except AttributeError as e:
            self._log.info("[dll-server] ... failed!")
            raise e
        except Exception as e:
            self._log.info("[dll-server] ... failed!")
            self._log.error(traceback.format_exc())
            raise e

        # Generate new instance of routine class
        self._routines[name] = RoutineServer(
            name,
            routine_handler,
            self._hash_id,
            self._convention,
            self._name,
            self._log,
            self._rpc_server,
            self._data,
        )

        self._log.info("[dll-server] ... done.")
