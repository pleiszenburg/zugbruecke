# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/interpreter.py: Class for managing Python interpreter on Wine

    Required to run on platform / side: [UNIX]

    Copyright (C) 2017-2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
import queue
import signal
import subprocess
import time
import threading


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE PYTHON INTERPRETER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class interpreter_session_class:

    # session init
    def __init__(self, session_id, parameter, session_log):

        # Set ID, parameters and pointer to log
        self.id = session_id
        self.p = parameter
        self.log = session_log

        # Log status
        self.log.out("[interpreter] STARTING ...")

        # Session is up
        self.up = True

        # Start wine python
        self.__python_start__()

        # Log status
        self.log.out("[interpreter] STARTED.")

    # session destructor
    def terminate(self):

        if not self.up:
            return

        # Log status
        self.log.out("[interpreter] TERMINATING ...")

        # Shut down wine python
        self.__python_stop__()

        # Shut down processing thread
        self.__thread_stop__()

        # Log status
        self.log.out("[interpreter] TERMINATED.")

        # Session is down
        self.up = False

    @staticmethod
    def __stream_worker__(in_stream, out_queue):
        """reads lines from stream and puts them into queue"""

        for line in iter(in_stream.readline, b""):
            out_queue.put(line)
        in_stream.close()

    @staticmethod
    def __start_stream_worker__(in_stream, worker_function):
        """starts reader thread and returns a thread object and a queue object"""

        out_queue = queue.Queue()
        reader_thread = threading.Thread(
            target=worker_function, args=(in_stream, out_queue)
        )
        reader_thread.daemon = True
        reader_thread.start()
        return reader_thread, out_queue

    @staticmethod
    def __read_stream__(in_queue, processing_function):
        """reads lines from queue and processes them"""

        try:
            line = in_queue.get_nowait()
        except queue.Empty:
            pass
        else:
            line = line.decode("utf-8")
            processing_function(line.strip("\n"))
            in_queue.task_done()

    def __processing_worker__(self):
        """reads lines from queues and puts them into process methods"""

        # Log status
        self.log.out("[interpreter] Starting log processing thread ...")

        while self.__is_alive__():
            time.sleep(0.1)
            while not self.stdout_queue.empty():
                interpreter_session_class.__read_stream__(
                    self.stdout_queue, lambda line: self.log.out("[P] " + line)
                )
            while not self.stderr_queue.empty():
                interpreter_session_class.__read_stream__(
                    self.stderr_queue, lambda line: self.log.err("[P] " + line)
                )

        # Log status
        self.log.out("[interpreter] Joining worker threads and queues ...")

        self.stdout_queue.join()
        self.stderr_queue.join()
        self.stdout_thread.join()
        self.stderr_thread.join()

        # Log status
        self.log.out("[interpreter] ... worker threads and queues joined.")

    def __is_alive__(self):

        return self.proc_winepython.poll() is None

    def __python_start__(self):

        # Log status
        self.log.out(
            "[interpreter] Command: " + " ".join(self.p["server_command_list"])
        )

        # Prepare environment for interpreter - inherit from settings of current session!
        envvar_dict = {
            k: os.environ[k] for k in os.environ.keys()
        }  # HACK Required for Travis CI
        envvar_update_dict = dict(
            WENV_ARCH=self.p["arch"],  # Architecture
            WENV_PYTHONVERSION=self.p["pythonversion"],  # Version of Wine Python
        )
        envvar_dict.update(envvar_update_dict)

        # Log status
        self.log.out("[interpreter] Environment: " + str(envvar_dict))

        # Fire up Wine-Python process
        self.proc_winepython = subprocess.Popen(
            ["wenv", "python", "-u"] + self.p["server_command_list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            start_new_session=True,
            close_fds=True,
            env=envvar_dict,
        )

        # Status log
        self.log.out("[interpreter] Started with PID %d." % self.proc_winepython.pid)

        # Log status
        self.log.out("[interpreter] Starting stream reader threads ...")

        # Start worker threads and queues for reading from streams
        (
            self.stdout_thread,
            self.stdout_queue,
        ) = interpreter_session_class.__start_stream_worker__(
            self.proc_winepython.stdout, interpreter_session_class.__stream_worker__
        )
        (
            self.stderr_thread,
            self.stderr_queue,
        ) = interpreter_session_class.__start_stream_worker__(
            self.proc_winepython.stderr, interpreter_session_class.__stream_worker__
        )

        # Log status
        self.log.out("[interpreter] Stream reader threads started.")

        # Start processing thread for pushing lines into log
        self.processing_thread = threading.Thread(target=self.__processing_worker__)
        self.processing_thread.daemon = True
        self.processing_thread.start()

        # Log status
        self.log.out("[interpreter] Log processing thread started.")

    def __python_stop__(self):

        self.log.out("[interpreter] Ensure process has terminated, waiting ...")

        # Time-step
        wait_for_seconds = 0.01
        # Timeout
        timeout_after_seconds = self.p["timeout_stop"]

        # Start waiting at ...
        started_waiting_at = time.time()
        # Wait for process
        while (
            self.__is_alive__()
            and started_waiting_at + timeout_after_seconds > time.time()
        ):
            time.sleep(wait_for_seconds)
        # Is process still alive?
        if self.__is_alive__():
            self.log.out(
                "[interpreter] ... did not terminate after %d seconds, sending SIGINT ..."
                % timeout_after_seconds
            )
            os.killpg(os.getpgid(self.proc_winepython.pid), signal.SIGINT)
        else:
            self.log.out(
                "[interpreter] ... terminated on its own after %.02f seconds."
                % (time.time() - started_waiting_at)
            )
            return

        # Start waiting at ...
        started_waiting_at = time.time()
        # Wait for process
        while (
            self.__is_alive__()
            and started_waiting_at + timeout_after_seconds > time.time()
        ):
            time.sleep(wait_for_seconds)
        # Is process still alive?
        if self.__is_alive__():
            self.log.out(
                "[interpreter] ... did not terminate after %d seconds, sending SIGTERM ..."
                % timeout_after_seconds
            )
            os.killpg(os.getpgid(self.proc_winepython.pid), signal.SIGTERM)
        else:
            self.log.out(
                "[interpreter] ... terminated with SIGINT after %.02f seconds."
                % (time.time() - started_waiting_at)
            )
            return

        # Is process still alive?
        if self.__is_alive__():
            self.log.out("[interpreter] ... failed to terminate with SIGTERM!")
            raise TimeoutError("interpreter process could not be terminated")
        else:
            self.log.out("[interpreter] ... terminated with SIGTERM.")
            return

    def __thread_stop__(self):

        timeout_after_seconds = self.p["timeout_stop"]

        self.log.out("[interpreter] Joining processing thread ...")

        # Joining thread ...
        self.processing_thread.join(timeout=timeout_after_seconds)
        if self.processing_thread.is_alive():
            self.log.out("[interpreter] ... failed to join thread!")
            raise TimeoutError("processing thread could not be terminated")

        # Log status
        self.log.out("[interpreter] ... joined.")
