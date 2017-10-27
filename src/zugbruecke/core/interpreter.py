# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/interpreter.py: Class for managing Python interpreter on Wine

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
import signal
import subprocess
import threading


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE PYTHON INTERPRETER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class interpreter_session_class():


	# session init
	def __init__(self, session_id, parameter, session_log):

		# Set ID, parameters and pointer to log
		self.id = session_id
		self.p = parameter
		self.log = session_log

		# Log status
		self.log.out('[interpreter] STARTING ...')

		# Session is up
		self.up = True

		# Start wine python
		self.__python_start__(self.__compile_python_command__())

		# Log status
		self.log.out('[interpreter] STARTED.')


	# session destructor
	def terminate(self):

		if self.up:

			# Log status
			self.log.out('[interpreter] TERMINATING ...')

			# Shut down wine python
			self.__python_stop__()

			# Log status
			self.log.out('[interpreter] TERMINATED.')

			# Session is down
			self.up = False


	def __compile_python_command__(self):

		# Python interpreter's directory seen from this script
		dir_python = os.path.join(self.p['dir'], self.p['arch'] + '-python' + self.p['version'])

		# Identify wine command for 32 or 64 bit
		if self.p['arch'] == 'win32':
			wine_cmd = 'wine'
		elif self.p['arch'] == 'win64':
			wine_cmd = 'wine64'
		else:
			raise # TODO error

		# Prepare full python interpreter command
		return [wine_cmd, os.path.join(dir_python, 'python.exe')] + self.p['command_dict']


	def __read_output_from_pipe__(self, pipe, func):

		for line in iter(pipe.readline, b''):
			func('[P] ' + line.decode('utf-8'))
		pipe.close()


	def __python_start__(self, command_list):

		# Log status
		self.log.out('[interpreter] Command: ' + ' '.join(command_list))

		# Fire up Wine-Python process
		self.proc_winepython = subprocess.Popen(
			command_list,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = False,
			preexec_fn = os.setsid,
			close_fds = True,
			bufsize = 1
			)

		# Status log
		self.log.out('[interpreter] Started with PID %d.' % self.proc_winepython.pid)

		# Prepare threads for stdout and stderr capturing of Wine
		# BUG does not capture stdout from windows binaries (running with Wine) most of the time
		self.thread_winepython_out = threading.Thread(
			target = self.__read_output_from_pipe__,
			args = (self.proc_winepython.stdout, self.log.out),
			name = 'out'
			)
		self.thread_winepython_err = threading.Thread(
			target = self.__read_output_from_pipe__,
			args = (self.proc_winepython.stderr, self.log.err),
			name = 'err'
			)

		# Start threads
		for t in (self.thread_winepython_out, self.thread_winepython_err):
			t.daemon = True
			t.start()

		# Log status
		self.log.out('[interpreter] Logging threads started.')


	def __python_stop__(self):

		# Terminate Wine-Python
		os.killpg(os.getpgid(self.proc_winepython.pid), signal.SIGINT)

		for t_index, t in enumerate([self.thread_winepython_out, self.thread_winepython_err]):
			self.log.out('[interpreter] Joining logging thread "%s" ...' % t.name)
			t.join(timeout = 1) # seconds

		# Log status
		self.log.out('[interpreter] Logging threads joined or timed out.')
