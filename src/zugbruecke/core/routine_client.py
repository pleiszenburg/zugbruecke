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
        self._memsync = []
        self._memsync_d = None

        # By default, assume no arguments
        self._argtypes = []
        self._argtypes_d = None

        # By default, assume c_int return value like ctypes expects
        self._restype = ctypes.c_int
        self._restype_d = None

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

        # Handle memory
        mem_package_list = self._data.client_pack_memory_list(args, self._memsync_d)

        # Actually call routine in DLL! TODO Handle kw ...
        return_dict = self._call_on_server(
            self._data.arg_list_pack(args, self._argtypes_d, self._convention),
            mem_package_list,
        )

        self._log.out(
            "[routine-client] ... received feedback from server, unpacking & syncing arguments ..."
        )

        # Unpack return dict (call may have failed partially only)
        self._data.arg_list_sync(
            args,
            self._data.arg_list_unpack(
                return_dict["args"],
                self._argtypes_d,
                self._convention,
            ),
            self._argtypes_d,
        )

        self._log.out("[routine-client] ... unpacking return value ...")

        # Unpack return value of routine
        return_value = self._data.return_msg_unpack(
            return_dict["return_value"], self._restype_d
        )

        self._log.out("[routine-client] ... overwriting memory ...")

        # Unpack memory (call may have failed partially only)
        self._data.client_unpack_memory_list(
            args, return_value, return_dict["memory"], self._memsync_d
        )

        self._log.out("[routine-client] ... everything unpacked and overwritten ...")

        # Raise the original error if call was not a success
        if not return_dict["success"]:
            self._log.out("[routine-client] ... call raised an error.")
            raise return_dict["exception"]

        self._log.out("[routine-client] ... return.")

        # Return result. return_value will be None if there was not a result.
        return return_value

    def __repr__(self) -> str:

        return self._get_repr_on_server()

    def _configure(self):

        self._log.out(
            "[routine-client] ... has not been called before. Configuring ..."
        )

        # Prepare list of arguments by parsing them into list of dicts (TODO field name / kw)
        self._argtypes_d = self._data.pack_definition_argtypes(self._argtypes)

        # Parse return type
        self._restype_d = self._data.pack_definition_returntype(self._restype)

        # Compile memsync statements HACK just unpack the user input ...
        self._memsync_d = self._data.unpack_definition_memsync(self._memsync)

        # Pack memsync_d again for shipping
        memsync_d_packed = self._data.pack_definition_memsync(self._memsync_d)

        # Adjust definitions with void pointers
        self._data.apply_memsync_to_argtypes_and_restype_definition(
            self._memsync_d, self._argtypes_d, self._restype_d
        )

        # Log status
        self._log.out("<memsync>", self._memsync_d, "</memsync>")
        self._log.out("<argtypes>", self._argtypes, "</argtypes>")
        self._log.out("<argtypes_d>", self._argtypes_d, "</argtypes_d>")
        self._log.out("<restype>", self._restype, "</restype>")
        self._log.out("<restype_d>", self._restype_d, "</restype_d>")

        # Pass argument and return value types as strings ...
        _ = self._configure_on_server(
            self._argtypes_d, self._restype_d, memsync_d_packed
        )

        # Change status of routine - it has been called once and is therefore configured
        self._configured = True

        # Log status
        self._log.out("[routine-client] ... configured. Proceeding ...")

    @property
    def argtypes(self) -> Union[List, Tuple]:

        return self._argtypes

    @argtypes.setter
    def argtypes(self, value: Union[List, Tuple]):

        if not isinstance(value, list) and not isinstance(value, tuple):
            raise TypeError  # original ctypes does that

        self._argtypes = value

    @property
    def restype(self) -> Any:

        return self._restype

    @restype.setter
    def restype(self, value: Any):

        self._restype = value

    @property
    def memsync(self) -> List:

        return self._memsync

    @memsync.setter
    def memsync(self, value: List):

        if not isinstance(value, list):
            raise DataMemsyncsyntaxError("memsync attribute must be a list")

        self._memsync = value
