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

from .abc import (
    CallbackServerABC,
    DataABC,
    LogABC,
    RpcClientABC,
)
from .definitions import DefinitionMemsync
from .mempkg import Mempkg
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
        argtypes: List[Dict],
        restype: Dict,
        memsyncs: List[DefinitionMemsync],
    ):

        self._name = name
        self._handler = getattr(rpc_client, name)
        self._data = data
        self._log = log
        self._argtypes = argtypes
        self._restype = restype
        self._memsyncs = memsyncs

    def __call__(self, *args: Any) -> Any:

        args = list(args)

        self._log.out(
            '[callback-server] Trying to call callback routine "{NAME:s}" ...'.format(NAME = self._name)
        )
        self._log.out(
            '[callback-server] ... parameters are "{ARGS:s}". Packing and pushing to client ...'.format(ARGS = pf(args))
        )

        try:
            packed_args = self._data.pack_args(args, self._argtypes)
            packed_mempkgs = [mempkg.as_packed() for mempkg in DefinitionMemsync.pkg_memories(
                args = args,
                memsyncs = self._memsyncs,
            )]
        except Exception as e:
            self._log.out("[callback-server] ... memory packing failed!")
            self._log.err(traceback.format_exc())
            raise e

        try:
            return_package = self._handler(packed_args, packed_mempkgs)
        except Exception as e:
            self._log.out("[callback-server] ... call failed!")
            self._log.err(traceback.format_exc())
            raise e

        try:
            self._log.out(
                "[callback-server] ... received feedback from client, unpacking ..."
            )
            self._data.sync_args(
                args,
                self._data.unpack_args(return_package["args"], self._argtypes),
                self._argtypes,
            )
            retval = self._data.unpack_retval(
                return_package["retval"], self._restype
            )
            DefinitionMemsync.unpkg_memories(
                args = args,
                retval = retval,
                mempkgs = [Mempkg.from_packed(mempkg) for mempkg in return_package["mempkgs"]],
                memsyncs = self._memsyncs,
            )
        except Exception as e:
            self._log.out("[callback-server] ... unpacking failed!")
            self._log.err(traceback.format_exc())
            raise e

        if not return_package["success"]:
            self._log.out("[callback-server] ... call raised an error.")
            raise return_package["exception"]

        self._log.out("[callback-server] ... unpacked, return.")

        return retval
