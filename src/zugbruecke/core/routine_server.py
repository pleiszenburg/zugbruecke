# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/routine_server.py: Classes for managing routines in DLLs

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

from ctypes import _CFuncPtr
from pprint import pformat as pf
import traceback
from typing import Dict, List, Union

from .abc import DataABC, LogABC, RoutineServerABC, RpcServerABC
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class RoutineServer(RoutineServerABC):
    """
    Representing a routine in a DLL
    """

    def __init__(
        self,
        name: Union[str, int],
        handler: _CFuncPtr,
        hash_id: str,
        convention: str,
        dll_name: str,
        log: LogABC,
        rpc_server: RpcServerABC,
        data: DataABC,
    ):

        self._name = name
        self._handler = handler

        self._convention = convention
        self._dll_name = dll_name

        self._log = log
        self._data = data

        self._argtypes_d = None
        self._restype_d = None
        self._memsync_d = None

        for attr in (
            "call",
            "configure",
            "get_repr",
        ):
            rpc_server.register_function(
                getattr(self, attr),
                "{HASH_ID:s}_{NAME:s}_{ATTR:s}".format(
                    HASH_ID=hash_id, NAME=str(self._name), ATTR=attr
                ),
            )

    def call(self, arg_message_list: List, arg_memory_list: List) -> Dict:
        """
        Called by routine client
        """

        self._log.out(
            '[routine-server] Trying to call routine "{NAME:s}" in DLL file "{DLL_NAME:s}" ...'.format(
                NAME=str(self._name),
                DLL_NAME=self._dll_name,
            )
        )

        try:

            # Unpack passed arguments, handle pointers and structs ...
            args_list = self._data.arg_list_unpack(
                arg_message_list, self._argtypes_d, self._convention
            )

            # Unpack pointer data
            self._data.server_unpack_memory_list(
                args_list, arg_memory_list, self._memsync_d
            )

            # Default return value
            return_value = None

        except Exception as e:

            self._log.out("[routine-server] ... call preparation failed!")
            self._log.err(traceback.format_exc())

            raise e

        try:

            # Call into dll
            return_value = self._handler(*tuple(args_list))

        except Exception as e:

            self._log.out("[routine-server] ... call failed!")
            self._log.err(traceback.format_exc())

            # Pack return package and return it
            return {
                "args": arg_message_list,
                "return_value": return_value,
                "memory": arg_memory_list,
                "success": False,
                "exception": e,
            }

        try:

            # Pack memory for return
            self._data.server_pack_memory_list(
                args_list, return_value, arg_memory_list, self._memsync_d
            )

            # Get new arg message list
            arg_message_list = self._data.arg_list_pack(
                args_list, self._argtypes_d, self._convention
            )

            # Get new return message list
            return_message = self._data.return_msg_pack(return_value, self._restype_d)

            self._log.out("[routine-server] ... done.")

            # Pack return package and return it
            return {
                "args": arg_message_list,
                "return_value": return_message,
                "memory": arg_memory_list,
                "success": True,
                "exception": None,
            }

        except Exception as e:

            self._log.out("[routine-server] ... call post-processing failed!")
            self._log.err(traceback.format_exc())

            raise e

    def configure(self, argtypes_d: List, restype_d: Dict, memsync_d: List):
        """
        Called by routine client
        """

        # Store argtype definition dict
        self._argtypes_d = argtypes_d

        # Store return value definition dict
        self._restype_d = restype_d

        try:

            # Parse and apply argtype definition dict to actual ctypes routine
            _argtypes = self._data.unpack_definition_argtypes(argtypes_d)
            # Only configure if there are definitions, otherwise calls with int parameters without definition fail
            if len(_argtypes) > 0:
                self._handler.argtypes = _argtypes

            # Parse and apply restype definition dict to actual ctypes routine
            self._handler.restype = self._data.unpack_definition_returntype(restype_d)

            # Store memory sync instructions
            self._memsync_d = self._data.unpack_definition_memsync(memsync_d)

        except Exception as e:

            # Push traceback to log
            self._log.err(traceback.format_exc())

            raise e

        self._log.out(" memsync: \n%s" % pf(self._memsync_d))
        self._log.out(" argtypes: \n%s" % pf(self._handler.argtypes))
        self._log.out(" argtypes_d: \n%s" % pf(self._argtypes_d))
        self._log.out(" restype: \n%s" % pf(self._handler.restype))
        self._log.out(" restype_d: \n%s" % pf(self._restype_d))

    def get_repr(self) -> str:
        """
        Called by routine client
        """

        return repr(self._handler)
