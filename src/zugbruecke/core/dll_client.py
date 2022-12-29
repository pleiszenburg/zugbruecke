# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/dll_client.py: Classes for managing the access to DLLs

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

from typing import Union

from .abc import DataABC, DllClientABC, LogABC, RoutineClientABC, RpcClientABC
from .routine_client import RoutineClient
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class DllClient(DllClientABC):
    """
    Representing one idividual dll to be called into, returned by LoadLibrary
    """

    def __init__(
        self,
        name: str,
        hash_id: str,
        convention: str,
        log: LogABC,
        rpc_client: RpcClientABC,
        data: DataABC,
    ):

        self._name = name
        self._hash_id = hash_id
        self._convention = convention

        self._log = log
        self._rpc_client = rpc_client
        self._data = data

        self._routines = {}

        for name in (
            "get_repr",
            "register_routine",
        ):
            setattr(
                self,
                f"_{name:s}_on_server",
                getattr(
                    self._rpc_client,
                    f"{self._hash_id:s}_{name:s}",
                ),
            )

    def __getattr__(self, name: str) -> RoutineClientABC:

        if name in ("__objclass__", "__name__"):
            raise AttributeError(name)

        if name not in self._routines.keys():
            self._register_routine(name)

        return self._routines[name]

    def __getitem__(self, name_or_ordinal: Union[str, int]) -> RoutineClientABC:

        if name_or_ordinal not in self._routines.keys():
            self._register_routine(name_or_ordinal)

        return self._routines[name_or_ordinal]

    def __repr__(self) -> str:

        return self._get_repr_on_server()

    def _register_routine(self, name: Union[str, int]):

        self._log.info(f'[dll-client] Trying to register routine "{str(name):s}" in DLL file "{self._name:s}" ...')

        try:
            self._register_routine_on_server(name)
        except AttributeError as e:
            self._log.info("[dll-client] ... failed!")
            raise e

        self._routines[name] = RoutineClient(
            name,
            self._hash_id,
            self._convention,
            self._name,
            self._log,
            self._rpc_client,
            self._data,
        )

        self._log.info("[dll-client] ... registered (unconfigured).")
