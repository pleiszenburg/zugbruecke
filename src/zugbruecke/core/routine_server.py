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
from typing import Any, Dict, List, Union

from .abc import DataABC, LogABC, RoutineServerABC, RpcServerABC
from .definitions import Definition, DefinitionMemsync
from .mempkg import Mempkg
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

        self._argtypes = None
        self._restype = None
        self._memsyncs = None

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

    def call(self, packed_args: List[Any], packed_mempkgs: List[Dict]) -> Dict:
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
            args = self._data.unpack_args(
                packed_args, self._argtypes, self._convention
            )
            retval = None
            mempkgs = [Mempkg.from_packed(packed_mempkg) for packed_mempkg in packed_mempkgs]
            DefinitionMemsync.unpkg_memories(
                args = args,
                retval = retval,
                mempkgs = mempkgs,
                memsyncs = self._memsyncs,
                is_server = True,
            )
        except Exception as e:
            self._log.out("[routine-server] ... call preparation failed!")
            self._log.err(traceback.format_exc())
            raise e

        try:
            retval = self._handler(*args)
        except Exception as e:
            self._log.out("[routine-server] ... call failed!")
            self._log.err(traceback.format_exc())
            return {
                "args": packed_args,  # unchanged
                "retval": retval,  # unchanged, still None
                "mempkgs": packed_mempkgs,  # unchanged
                "success": False,
                "exception": e,
            }

        try:
            DefinitionMemsync.update_memories(
                args = args,
                retval = retval,
                mempkgs = mempkgs,
                memsyncs = self._memsyncs,
            )
            self._log.out("[routine-server] ... done.")
            return {
                "args": self._data.pack_args(args, self._argtypes, self._convention),
                "retval": self._data.pack_retval(retval, self._restype),
                "mempkgs": [mempkg.as_packed() for mempkg in mempkgs],
                "success": True,
                "exception": None,
            }
        except Exception as e:
            self._log.out("[routine-server] ... call post-processing failed!")
            self._log.err(traceback.format_exc())
            raise e

    def configure(self, packed_argtypes: List[Dict], packed_restype: Dict, packed_memsyncs: List[Dict]):
        """
        Called by routine client
        """

        try:

            # Unpack argtype definitions
            self._argtypes = [
                Definition.from_packed(
                    packed = packed_argtype,
                    cache = self._data.cache,
                )
                for packed_argtype in packed_argtypes
            ]

            # Unpack return type definition
            self._restype = Definition.from_packed(
                packed = packed_restype,
                cache = self._data.cache,
            )

            # Unpack memory sync definitions
            self._memsyncs = [
                DefinitionMemsync.from_packed(
                    packed = packed_memsync,
                    cache = self._data.cache,
                )
                for packed_memsync in packed_memsyncs
            ]

            # Parse and apply argtype definition dict to actual ctypes routine
            argtypes = [argtype.data_type for argtype in self._argtypes]
            # Only configure if there are definitions, otherwise calls with int parameters without definition fail
            if len(argtypes) > 0:
                self._handler.argtypes = argtypes

            # Parse and apply restype definition dict to actual ctypes routine
            self._handler.restype = self._restype.data_type

        except Exception as e:

            # Push traceback to log
            self._log.err(traceback.format_exc())

            raise e

        self._log.out(f" memsyncs: \n{pf(self._memsyncs):s}")
        self._log.out(f" handler.argtypes: \n{pf(self._handler.argtypes):s}")
        self._log.out(f" argtypes: \n{pf(self._argtypes):s}")
        self._log.out(f" handler.restype: \n{pf(self._handler.restype):s}")
        self._log.out(f" restype: \n{pf(self._restype):s}")

    def get_repr(self) -> str:
        """
        Called by routine client
        """

        return repr(self._handler)
