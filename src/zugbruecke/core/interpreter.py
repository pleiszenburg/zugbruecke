# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/interpreter.py: Class for managing Python interpreter on Wine

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

import os
from queue import Queue, Empty
import signal
import subprocess
import time
from typing import BinaryIO, Callable, Dict, Tuple
from threading import Thread

from wenv import EnvConfig

from .abc import ConfigABC, InterpreterABC, LogABC
from .lib import get_free_port
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE PYTHON INTERPRETER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Interpreter(InterpreterABC):
    """
    Class for managing Python interpreter on Wine
    """

    def __init__(self, session_id: str, parameter: ConfigABC, session_log: LogABC):

        # Set ID, parameters and pointer to log
        self._id = session_id
        self._p = parameter
        self._log = session_log

        # Log status
        self._log.info("[interpreter] STARTING ...")

        # Session is up
        self._up = True

        # Start wine python
        self._python_start()

        # Log status
        self._log.info("[interpreter] STARTED.")

    # session destructor
    def terminate(self):

        if not self._up:
            return

        # Log status
        self._log.info("[interpreter] TERMINATING ...")

        # Shut down wine python
        self._python_stop()

        # Shut down processing thread
        self._thread_stop()

        # Log status
        self._log.info("[interpreter] TERMINATED.")

        # Session is down
        self._up = False

    @staticmethod
    def _stream_worker(in_stream: BinaryIO, out_queue: Queue):
        """reads lines from stream and puts them into queue"""

        for line in iter(in_stream.readline, b""):
            out_queue.put(line)
        in_stream.close()

    @staticmethod
    def _start_stream_worker(
        in_stream: BinaryIO, worker_function: Callable
    ) -> Tuple[Thread, Queue]:
        """starts reader thread and returns a thread object and a queue object"""

        out_queue = Queue()
        reader_thread = Thread(target=worker_function, args=(in_stream, out_queue))
        reader_thread.daemon = True
        reader_thread.start()
        return reader_thread, out_queue

    @staticmethod
    def _read_stream(in_queue: Queue, processing_function: Callable):
        """reads lines from queue and processes them"""

        try:
            line = in_queue.get_nowait()
        except Empty:
            pass
        else:
            line = line.decode("utf-8")
            processing_function(line.strip("\n"))
            in_queue.task_done()

    def _processing_worker(self):
        """reads lines from queues and puts them into process methods"""

        # Log status
        self._log.info("[interpreter] Starting log processing thread ...")

        while self._is_alive():
            time.sleep(0.1)
            while not self._stdout_queue.empty():
                self._read_stream(
                    self._stdout_queue, lambda line: self._log.debug(f"[P] {line:s}")
                )
            while not self._stderr_queue.empty():
                self._read_stream(
                    self._stderr_queue, lambda line: self._log.error(f"[P] {line:s}")
                )

        # Log status
        self._log.info("[interpreter] Joining worker threads and queues ...")

        self._stdout_queue.join()
        self._stderr_queue.join()
        self._stdout_thread.join()
        self._stderr_thread.join()

        # Log status
        self._log.info("[interpreter] ... worker threads and queues joined.")

    def _is_alive(self) -> bool:

        return self._proc_winepython.poll() is None

    def _set_cli_params(self):

        # Get socket for ctypes bridge
        self._p["port_socket_wine"] = get_free_port()

        # Prepare command with minimal meta info. All other info can be passed via sockets.
        self._p["server_cli_params"] = [
            "-m",
            "zugbruecke._server_",
            "--id",
            self._id,
            "--port_socket_wine",
            str(self._p["port_socket_wine"]),
            "--port_socket_unix",
            str(self._p["port_socket_unix"]),
            "--log_level",
            str(self._p["log_level"]),
            "--log_write",
            str(int(self._p["log_write"])),
            "--timeout_start",
            str(int(self._p["timeout_start"])),
        ]

    def _get_env(self) -> Dict[str, str]:
        """
        Prepare environment for interpreter - inherit from settings of current session!
        """

        env = os.environ.copy()
        env.update(EnvConfig(**self._p.export_dict()).export_envvar_dict())

        if os.environ.get('ZUGBRUECKE_DEBUG', '0') == '1':
            env['COVERAGE_PROCESS_START'] = 'pyproject.toml'

        return env

    def _python_start(self):

        self._set_cli_params()
        env = self._get_env()

        # Log status
        self._log.info(f'[interpreter] Command: {" ".join(self._p["server_cli_params"]):s}')

        # Log status
        self._log.info(f"[interpreter] Environment: {str(env):s}")

        # Fire up Wine-Python process
        self._proc_winepython = subprocess.Popen(
            ["wenv", "python", "-u"] + self._p["server_cli_params"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            start_new_session=True,
            close_fds=True,
            env=env,
        )

        # Status log
        self._log.info(f"[interpreter] Started with PID {self._proc_winepython.pid:d}.")

        # Log status
        self._log.info("[interpreter] Starting stream reader threads ...")

        # Start worker threads and queues for reading from streams
        (
            self._stdout_thread,
            self._stdout_queue,
        ) = self._start_stream_worker(self._proc_winepython.stdout, self._stream_worker)
        (
            self._stderr_thread,
            self._stderr_queue,
        ) = self._start_stream_worker(self._proc_winepython.stderr, self._stream_worker)

        # Log status
        self._log.info("[interpreter] Stream reader threads started.")

        # Start processing thread for pushing lines into log
        self._processing_thread = Thread(target=self._processing_worker)
        self._processing_thread.daemon = True
        self._processing_thread.start()

        # Log status
        self._log.info("[interpreter] Log processing thread started.")

    def _python_stop(self):

        self._log.info("[interpreter] Ensure process has terminated, waiting ...")

        # Time-step
        wait_for_seconds = 0.01
        # Timeout
        timeout_after_seconds = self._p["timeout_stop"]

        # Start waiting at ...
        started_waiting_at = time.time()
        # Wait for process
        while (
            self._is_alive()
            and started_waiting_at + timeout_after_seconds > time.time()
        ):
            time.sleep(wait_for_seconds)
        # Is process still alive?
        if self._is_alive():
            self._log.warning(f"[interpreter] ... did not terminate after {timeout_after_seconds:d} seconds, sending SIGINT ...")
            os.killpg(os.getpgid(self._proc_winepython.pid), signal.SIGINT)
        else:
            self._log.info(f"[interpreter] ... terminated on its own after {time.time() - started_waiting_at:.02f} seconds.")
            return

        # Start waiting at ...
        started_waiting_at = time.time()
        # Wait for process
        while (
            self._is_alive()
            and started_waiting_at + timeout_after_seconds > time.time()
        ):
            time.sleep(wait_for_seconds)
        # Is process still alive?
        if self._is_alive():
            self._log.warning(f"[interpreter] ... did not terminate after {timeout_after_seconds:d} seconds, sending SIGTERM ...")
            os.killpg(os.getpgid(self._proc_winepython.pid), signal.SIGTERM)
        else:
            self._log.warning(f"[interpreter] ... terminated with SIGINT after {time.time() - started_waiting_at:.02f} seconds.")
            return

        # Is process still alive?
        if self._is_alive():
            self._log.error("[interpreter] ... failed to terminate with SIGTERM!")
            raise TimeoutError("interpreter process could not be terminated")
        else:
            self._log.warning("[interpreter] ... terminated with SIGTERM.")
            return

    def _thread_stop(self):

        timeout_after_seconds = self._p["timeout_stop"]

        self._log.info("[interpreter] Joining processing thread ...")

        # Joining thread ...
        self._processing_thread.join(timeout=timeout_after_seconds)
        if self._processing_thread.is_alive():
            self._log.error("[interpreter] ... failed to join thread!")
            raise TimeoutError("processing thread could not be terminated")

        # Log status
        self._log.info("[interpreter] ... joined.")
