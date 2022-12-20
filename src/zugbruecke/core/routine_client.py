# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/routine_client.py: Classes for managing routines in DLLs

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

import ctypes
from pprint import pformat as pf
from typing import Any, List, Tuple, Union

from .abc import DataABC, LogABC, RoutineClientABC, RpcClientABC
from .data import Mempkg
from .definitions import DefinitionMemsync
from .errors import DataMemsyncsyntaxError
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class RoutineClient(RoutineClientABC):
    """
    Representing a routine in a DLL
    """

    def __init__(
        self,
        name: Union[str, int],
        hash_id: str,
        convention: str,
        dll_name: str,
        log: LogABC,
        rpc_client: RpcClientABC,
        data: DataABC,
    ):

        self._name = name

        self._convention = convention
        self._dll_name = dll_name
        self._log = log
        self._data = data

        # Set call status
        self._configured = False

        # By default, there is no memory to sync
        self._memsyncs_raw = []
        self._memsyncs = None

        # By default, assume no arguments
        self._argtypes_raw = []
        self._argtypes = None

        # By default, assume c_int return value like ctypes expects
        self._restype_raw = ctypes.c_int
        self._restype = None

        for attr in (
            "call",
            "configure",
            "get_repr",
        ):
            setattr(
                self,
                "_{ATTR:s}_on_server".format(ATTR=attr),
                getattr(
                    rpc_client,
                    "{HASH_ID:s}_{NAME:s}_{ATTR:s}".format(
                        HASH_ID=hash_id, NAME=str(self._name), ATTR=attr
                    ),
                ),
            )

    def __call__(self, *args: Any) -> Any:
        """
        TODO Optimize for speed!
        """

        args = list(args)

        self._log.out(
            '[routine-client] Trying to call routine "{NAME:s}" in DLL file "{DLL_NAME:s}" ...'.format(
                NAME=str(self._name),
                DLL_NAME=self._dll_name,
            )
        )

        if not self._configured:
            self._configure()

        self._log.out(
            '[routine-client] ... parameters are "{ARGS:s}". Packing and pushing to server ...'.format(
                ARGS=pf(args)
            )
        )

        # Pack stuff
        packed_args = self._data.pack_args(args, self._argtypes, self._convention)
        packed_mempkgs = [mempkg.as_packed() for mempkg in DefinitionMemsync.pkg_memories(
            args = args,
            memsyncs = self._memsyncs,
        )]

        # Actually call routine in DLL
        return_package = self._call_on_server(packed_args, packed_mempkgs)

        self._log.out(
            "[routine-client] ... received feedback from server, unpacking & syncing arguments ..."
        )

        # Unpack return dict (call may have failed partially only)
        self._data.sync_args(
            args,
            self._data.unpack_args(
                return_package["args"],
                self._argtypes,
                self._convention,
            ),
            self._argtypes,
        )

        self._log.out("[routine-client] ... unpacking return value ...")

        # Unpack return value of routine
        retval = self._data.unpack_retval(
            return_package["retval"], self._restype
        )

        self._log.out("[routine-client] ... overwriting memory ...")

        # Unpack memory (call may have failed partially only)
        DefinitionMemsync.unpkg_memories(
            args = args,
            retval = retval,
            mempkgs = [Mempkg.from_packed(mempkg) for mempkg in return_package["mempkgs"]],
            memsyncs = self._memsyncs,
        )

        self._log.out("[routine-client] ... everything unpacked and overwritten ...")

        # Raise the original error if call was not a success
        if not return_package["success"]:
            self._log.out("[routine-client] ... call raised an error.")
            raise return_package["exception"]

        self._log.out("[routine-client] ... return.")

        # Return result. return_value will be None if there was not a result.
        return retval

    def __repr__(self) -> str:

        return self._get_repr_on_server()

    def _configure(self):

        self._log.out(
            "[routine-client] ... has not been called before. Configuring ..."
        )

        # Prepare list of arguments by parsing them into list of dicts (TODO field name / kw)
        self._argtypes = self._data.pack_definition_argtypes(self._argtypes_raw)

        # Parse return type
        self._restype = self._data.pack_definition_returntype(self._restype_raw)

        # Compile memsync statements
        self._memsyncs = DefinitionMemsync.from_raws(
            definitions = self._memsyncs_raw,
            cache = self._data.cache,
        )

        # Adjust definitions with void pointers
        DefinitionMemsync.apply_multiple(
            memsyncs = self._memsyncs,
            argtypes = self._argtypes,
            restype = self._restype,
        )

        # Log status
        self._log.out("<memsync_raw>", self._memsyncs_raw, "</memsync_raw>")
        self._log.out("<memsync>", self._memsyncs, "</memsync>")
        self._log.out("<argtypes_raw>", self._argtypes_raw, "</argtypes_raw>")
        self._log.out("<argtypes>", self._argtypes, "</argtypes>")
        self._log.out("<restype_raw>", self._restype_raw, "</restype_raw>")
        self._log.out("<restype>", self._restype, "</restype>")

        # Pack memsync_d again for shipping
        packed_memsyncs = [memsync.as_packed() for memsync in self._memsyncs]

        # Pass argument and return value types as strings ...
        _ = self._configure_on_server(
            self._argtypes, self._restype, packed_memsyncs
        )

        # Change status of routine - it has been called once and is therefore configured
        self._configured = True

        # Log status
        self._log.out("[routine-client] ... configured. Proceeding ...")

    @property
    def argtypes(self) -> Union[List, Tuple]:

        return self._argtypes_raw

    @argtypes.setter
    def argtypes(self, value: Union[List, Tuple]):

        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError  # original ctypes does that

        self._argtypes_raw = value

    @property
    def restype(self) -> Any:

        return self._restype_raw

    @restype.setter
    def restype(self, value: Any):

        self._restype_raw = value

    @property
    def memsync(self) -> List:

        return self._memsyncs_raw

    @memsync.setter
    def memsync(self, value: List):

        if not isinstance(value, list):
            raise DataMemsyncsyntaxError("memsync attribute must be a list")

        self._memsyncs_raw = value
