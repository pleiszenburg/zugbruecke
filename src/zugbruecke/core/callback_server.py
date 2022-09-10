# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/callback_server.py: Classes for managing callback routines

    Required to run on platform / side: [UNIX, WINE]

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

from pprint import pformat as pf
import traceback
from typing import Any, Dict, List

from .abc import CallbackServerABC, DataABC, LogABC, RpcClientABC
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CALLBACK SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class CallbackServer(CallbackServerABC):
    """
    Representing a callback function
    """

    def __init__(
        self,
        name: str,
        rpc_client: RpcClientABC,
        data: DataABC,
        log: LogABC,
        argtypes_d: List,
        restype_d: Dict,
        memsync_d: List,
    ):

        self._name = name
        self._handler = getattr(rpc_client, name)
        self._data = data
        self._log = log
        self._argtypes_d = argtypes_d
        self._restype_d = restype_d
        self._memsync_d = memsync_d

    def __call__(self, *args: Any) -> Any:

        self._log.out(
            '[callback-server] Trying to call callback routine "{NAME:s}" ...'.format(NAME = self._name)
        )
        self._log.out(
            '[callback-server] ... parameters are "{ARGS:s}". Packing and pushing to client ...'.format(ARGS = pf(args))
        )

        try:
            mem_package_list = self._data.client_pack_memory_list(args, self._memsync_d)
        except Exception as e:
            self._log.out("[callback-server] ... memory packing failed!")
            self._log.err(traceback.format_exc())
            raise e

        try:
            return_dict = self._handler(
                self._data.arg_list_pack(args, self._argtypes_d), mem_package_list
            )
        except Exception as e:
            self._log.out("[callback-server] ... call failed!")
            self._log.err(traceback.format_exc())
            raise e

        try:
            self._log.out(
                "[callback-server] ... received feedback from client, unpacking ..."
            )
            self._data.arg_list_sync(
                args,
                self._data.arg_list_unpack(return_dict["args"], self._argtypes_d),
                self._argtypes_d,
            )
            return_value = self._data.return_msg_unpack(
                return_dict["return_value"], self._restype_d
            )
            self._data.client_unpack_memory_list(
                args, return_value, return_dict["memory"], self._memsync_d
            )
        except Exception as e:
            self._log.out("[callback-server] ... unpacking failed!")
            self._log.err(traceback.format_exc())
            raise e

        if not return_dict["success"]:
            self._log.out("[callback-server] ... call raised an error.")
            raise return_dict["exception"]

        self._log.out("[callback-server] ... unpacked, return.")

        return return_value
