# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/_server_.py: Class(es) for managing Python interpreter on Wine

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/s-m-e/pycrosscall/blob/master/LICENSE

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
import time


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE PYTHON INTERPRETER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class interpreter_session_class():


	# session init
	def __init__(self, session_id, parameter, session_log, session_wineserver):

		# Set ID, parameters and pointer to log
		self.id = session_id
		self.p = parameter
		self.log = session_log
		self.wineserver = session_wineserver

		# Fire session up
		self.__session_start__()


	# flow control routine for setting things up, called once from init
	def __session_start__(self):

		# Log status
		self.log.out('[interpreter session] starting ...')

		# Session is up
		self.up = True

		# Start wine python
		self.__wine_python_start__(self.__compile_wine_python_command__())

		# Log status
		self.log.out('[interpreter session] started')


	# session destructor
	def terminate(self):

		if self.up:

			# Log status
			self.log.out('[wine session] terminating ...')

			# Shut down wine python
			self.__wine_python_stop__()

			# Log status
			self.log.out('[wine session] terminated')

			# Session is down
			self.up = False


	def __compile_wine_python_command__(self):

		# Get location of this script file
		dir_thisfile = get_location_of_file(__file__)

		# Translate this file's Unix path into Wine path
		dir_thisfile_wine = self.wineserver.translate_path_unix2win(dir_thisfile)

		# Python interpreter's directory seen from this script
		dir_python = os.path.join(self.p['dir'], self.p['arch'] + '-python' + self.p['version'])

		# Identify wine command for 32 or 64 bit
		if self.p['arch'] == 'win32':
			wine_cmd = 'wine'
		elif self.p['arch'] == 'win64':
			wine_cmd = 'wine64'
		else:
			raise # TODO error

		# Prepare Wine-Python server command with session id and return it
		return [
			wine_cmd,
			os.path.join(dir_python, 'python.exe'),
			"%s\\_server_.py" % dir_thisfile_wine,
			'--id', self.id,
			'--port_in', str(self.p['port_wine']),
			'--port_out', str(self.p['port_unix']),
			'--log_level', str(self.p['log_level'])
			]


	def __read_output_from_pipe__(self, pipe, func):

		for line in iter(pipe.readline, b''):
			func('[P] ' + line.decode('utf-8'))
		pipe.close()


	def __wine_python_start__(self, command_list):

		# Log status
		self.log.out('wine-python command: ' + ' '.join(command_list))

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
		self.log.out('wine-python started with PID %d' % self.proc_winepython.pid)

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

		# HACK Wait ...
		time.sleep(1) # seconds

		# Log status
		self.log.out('threads for wine-python logging started')

		# Fire up xmlrpc client
		self.client = xmlrpc_client.ServerProxy('http://localhost:8000')

		# Log status
		self.log.out('xmlrpc-client started')


	def __wine_python_stop__(self):

		# Tell server via message to terminate
		self.client.terminate()

		# Terminate Wine-Python
		os.killpg(os.getpgid(self.proc_winepython.pid), signal.SIGINT)

		for t_index, t in enumerate([self.thread_winepython_out, self.thread_winepython_err]):
			self.log.out('joining thread "%s" ...' % t.name)
			t.join(timeout = 1) # seconds

		# HACK wait for its destructor
		time.sleep(1) # seconds
