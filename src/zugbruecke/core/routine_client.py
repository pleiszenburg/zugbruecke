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
from .definitions import Definition, DefinitionMemsync
from .mempkg import Mempkg
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
        self._restype_raw = None
        self._restype = None

        for attr in (
            "call",
            "configure",
            "get_repr",
        ):
            setattr(
                self,
                f"_{attr:s}_on_server",
                getattr(
                    rpc_client,
                    f"{hash_id:s}_{str(self._name):s}_{attr:s}",
                ),
            )

    def __call__(self, *args: Any) -> Any:
        """
        TODO Optimize for speed!
        """

        args = list(args)

        self._log.info(f'[routine-client] Trying to call routine "{str(self._name):s}" in DLL file "{self._dll_name:s}" ...')

        if not self._configured:
            self._configure()

        self._log.info('[routine-client] ... packing and pushing args to server ...')

        # Pack stuff
        packed_args = self._data.pack_args(args, self._argtypes, self._convention)
        mempkgs = DefinitionMemsync.pkg_memories(
            args = args,
            memsyncs = self._memsyncs,
        )  # keep until after function call to avoid pointers being garbage collected
        packed_mempkgs = [mempkg.as_packed() for mempkg in mempkgs]

        self._log.debug(dict(
            args = args,
            packed_args = packed_args,
            packed_mempkgs = packed_mempkgs,
        ))

        # Actually call routine in DLL
        return_package = self._call_on_server(packed_args, packed_mempkgs)

        self._log.info("[routine-client] ... received feedback from server, unpacking & syncing arguments ...")

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

        self._log.info("[routine-client] ... unpacking return value ...")

        # Unpack return value of routine
        retval = self._data.unpack_retval(
            return_package["retval"], self._restype
        )

        self._log.info("[routine-client] ... overwriting memory ...")

        # Unpack memory (call may have failed partially only)
        DefinitionMemsync.unpkg_memories(
            args = args,
            retval = retval,
            mempkgs = [Mempkg.from_packed(mempkg) for mempkg in return_package["mempkgs"]],
            memsyncs = self._memsyncs,
        )

        self._log.info("[routine-client] ... everything unpacked and overwritten ...")

        # Raise the original error if call was not a success
        if not return_package["success"]:
            self._log.error("[routine-client] ... call raised an error.")
            raise return_package["exception"]

        self._log.info("[routine-client] ... return.")

        # Return result. return_value will be None if there was not a result.
        return retval

    def __repr__(self) -> str:

        return self._get_repr_on_server()

    def _configure(self):

        self._log.info("[routine-client] ... has not been called before. Configuring ...")

        # Parse raw argtypes into definitions
        self._argtypes = Definition.from_data_types(
            cache = self._data.cache,
            data_types = self._argtypes_raw,
        )

        # Parse raw return type into definition
        self._restype = Definition.from_data_type(
            cache = self._data.cache,
            data_type = self._restype_raw,
        ) if self._restype_raw is not None else None

        # Parse memsync statements into definitions
        self._memsyncs = DefinitionMemsync.from_raws(
            definitions = self._memsyncs_raw,
            cache = self._data.cache,
        )

        # Adjust definitions with void pointers
        self._argtypes, self._restype = DefinitionMemsync.apply_many(
            cache = self._data.cache,
            memsyncs = self._memsyncs,
            argtypes = self._argtypes,
            restype = self._restype,
        )

        # Log status
        self._log.debug(dict(
            argtypes_raw = self._argtypes_raw,
            argtypes = self._argtypes,
            restype_raw = self._restype_raw,
            restype = self._restype,
            memsync_raw = self._memsyncs_raw,
            memsync = self._memsyncs,
        ))

        # Pass argument and return value types as strings ...
        _ = self._configure_on_server(
            [argtype.as_packed() for argtype in self._argtypes],
            self._restype.as_packed() if self._restype is not None else None,
            [memsync.as_packed() for memsync in self._memsyncs],
        )

        # Change status of routine - it has been called once and is therefore configured
        self._configured = True

        # Log status
        self._log.info("[routine-client] ... configured. Proceeding ...")

    @property
    def argtypes(self) -> Union[List, Tuple]:

        return self._argtypes_raw

    @argtypes.setter
    def argtypes(self, value: Union[List, Tuple]):

        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError  # original ctypes does that

        self._argtypes_raw = list(value)

    @property
    def restype(self) -> Any:

        return self._restype_raw

    @restype.setter
    def restype(self, value: Any):

        if isinstance(value, tuple) or isinstance(value, list):  # TODO better check for ctypes types?
            raise TypeError  # original ctypes does that

        self._restype_raw = value

    @property
    def memsync(self) -> List:

        return self._memsyncs_raw

    @memsync.setter
    def memsync(self, value: List):

        if not isinstance(value, list):
            raise TypeError("memsync attribute must be a list")

        self._memsyncs_raw = value
