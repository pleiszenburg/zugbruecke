# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/callback_client.py: Classes for managing callback routines

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

import traceback
from typing import Any, Callable, Dict, List

from .abc import (
    CallbackClientABC,
    DataABC,
    LogABC,
    RpcServerABC,
)
from .definitions import Definition, DefinitionMemsync
from .mempkg import Mempkg
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CALLBACK CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class CallbackClient(CallbackClientABC):
    """
    Representing a callback function
    """

    def __init__(
        self,
        name: str,
        handler: Callable,
        rpc_server: RpcServerABC,
        data: DataABC,
        log: LogABC,
        argtypes: List[Definition],
        restype: Definition,
        memsyncs: List[DefinitionMemsync],
    ):

        self._name = name
        self._handler = handler
        self._data = data
        self._log = log

        self._argtypes = argtypes
        self._restype = restype
        self._memsyncs = memsyncs

        rpc_server.register_function(self, public_name=name)

    def __call__(self, packed_args: List[Any], packed_mempkgs: List[Dict]) -> Dict:

        self._log.info(f'[callback-client] Trying to call callback routine "{self._name:s}" ...')

        try:
            args = self._data.unpack_args(packed_args, self._argtypes)
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
            self._log.error("[callback-client] ... call preparation failed!")
            self._log.error(traceback.format_exc())
            raise e

        try:
            retval = self._handler(*args)
        except Exception as e:
            self._log.error("[callback-client] ... call failed!")
            self._log.error(traceback.format_exc())
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
            self._log.info("[callback-client] ... done.")
            return {
                "args": self._data.pack_args(args, self._argtypes),
                "retval": self._data.pack_retval(retval, self._restype),
                "mempkgs": [mempkg.as_packed() for mempkg in mempkgs],
                "success": True,
                "exception": None,
            }
        except Exception as e:
            self._log.error("[callback-client] ... call post-processing failed!")
            self._log.error(traceback.format_exc())
            raise e
