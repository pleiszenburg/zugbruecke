# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/rpc.py: Customized RPC classes

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

from multiprocessing.connection import Client, Listener, _ConnectionBase
from threading import Thread
import time
import traceback
from typing import Any, Callable, Tuple, Union

from .abc import LogABC, RpcClientABC, RpcServerABC
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class RpcClient(RpcClientABC):
    """
    RPC client
    """

    def __init__(self, socket_path: Tuple[str, int], authkey: str):

        self._client = Client(socket_path, authkey=authkey.encode("utf-8"))
        self._cache = {}

    def __getattr__(self, name: str) -> Callable:

        try:
            return self._cache[name]
        except KeyError:
            pass

        def call_rpc_server(*args: Any, **kwargs: Any) -> Any:

            self._client.send((name, args, kwargs))
            result = self._client.recv()

            if isinstance(result, Exception):
                # TODO print traceback to stderr?
                raise result

            return result

        self._cache[name] = call_rpc_server
        return call_rpc_server

    @classmethod
    def from_safe_connect(
        cls,
        socket_path: Tuple[str, int],
        authkey: str,
        timeout_after_seconds: Union[int, float] = 30,
        wait_for_seconds: Union[int, float] = 0.01,
    ) -> RpcClientABC:

        started_waiting_at = time.time()

        while True:

            try:
                client = cls(socket_path, authkey)
                if client.get_rpc_status():
                    return client
            except:
                pass

            if time.time() >= (started_waiting_at + timeout_after_seconds):
                break

            time.sleep(wait_for_seconds)

        raise TimeoutError("rpc client failed to start")


@typechecked
class RpcServer(RpcServerABC):
    """
    RPC client
    """

    def __init__(
        self,
        socket_path: Tuple[str, int],
        authkey: str,
        log: Union[LogABC, None] = None,
        terminate_function: Union[Callable, None] = None,
    ):

        self._up = True
        self._log = log

        if self._log is not None:
            self._log.info("[rpc-server] STARTING ...")
            self._log.info("[rpc-server] Log attached.")

        self._socket_path = socket_path
        self._authkey = authkey.encode("utf-8")
        self._terminate_function = terminate_function

        self._server = None
        self._t = None

        self._functions = {}
        self.register_function(self.get_rpc_status)

        if self._log is not None:
            self._log.info("[rpc-server] STARTED.")

    def get_rpc_status(self) -> bool:
        """
        Called by RPC client
        """

        return self._up

    def register_function(
        self, function_pointer: Callable, public_name: Union[str, None] = None
    ):

        self._functions[
            function_pointer.__name__ if public_name is None else public_name
        ] = function_pointer

    def terminate(self):

        if not self._up:
            return

        self._up = False

        if self._log is not None:
            self._log.info("[rpc-server] TERMINATING ...")

        if self._terminate_function is not None:
            self._terminate_function()

        if self._log is not None:
            self._log.info("[rpc-server] TERMINATED.")

        self._server.close()

    def serve_forever(self):

        self._server = Listener(self._socket_path, authkey=self._authkey)

        while self._up:

            try:
                connection = self._server.accept()
                t = Thread(target=self._handle_connection, args=(connection,))
                t.daemon = True
                t.start()
            except OSError:
                if self._log is not None:
                    self._log.error("[rpc-server] OSError: Socket likely closed.")
            except Exception as e:
                traceback.print_exc()

    def server_forever_in_thread(self, daemon: bool = True):

        if self._t is not None:
            return

        self._t = Thread(target=self.serve_forever)
        self._t.daemon = daemon
        self._t.start()

    def _handle_connection(self, connection: _ConnectionBase):

        try:
            while True:
                function_name, args, kwargs = connection.recv()
                try:
                    r = self._functions[function_name](*args, **kwargs)
                    connection.send(r)
                except Exception as e:
                    connection.send(e)
        except EOFError:
            pass
