# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/session.py: Classes for managing zugbruecke sessions

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

import atexit
import os
import signal
import time

from .config import get_module_config
from .dll_client import dll_client_class
from .interpreter import interpreter_session_class
from .lib import (
	get_free_port,
	get_location_of_file
	)
from .log import log_class
from .rpc import (
	mp_client_class
	)
from .wineenv import setup_wine_python
from .wineserver import wineserver_session_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ZUGBRUECKE SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_client_class():


	def __init__(self, parameter = {}):

		# Fill empty parameters with default values and/or config file contents
		self.p = get_module_config(parameter)

		# Get and set session id
		self.id = self.p['id']

		# Start session logging
		self.log = log_class(self.id, self.p)

		# Log status
		self.log.out('[core] STARTING ...')
		self.log.out('[core] Configured Wine-Python version is %s for %s.' % (self.p['version'], self.p['arch']))
		self.log.out('[core] Log socket port: %d.' % self.p['port_socket_log_main'])

		# Store current working directory
		self.dir_cwd = os.getcwd()

		# Install wine-python
		setup_wine_python(self.p['arch'], self.p['version'], self.p['dir'])

		# Initialize Wine session
		self.wineserver_session = wineserver_session_class(self.id, self.p, self.log)

		# Prepare python command for ctypes server or interpreter
		self.__prepare_python_command__()

		# Initialize interpreter session
		self.interpreter_session = interpreter_session_class(self.id, self.p, self.log, self.wineserver_session)

		# Set up a dict for loaded dlls
		self.dll_dict = {}

		# If in ctypes mode ...
		self.__start_ctypes_client__()

		# Mark session as up
		self.up = True

		# Register session destructur
		atexit.register(self.terminate)
		signal.signal(signal.SIGINT, self.terminate)
		signal.signal(signal.SIGTERM, self.terminate)

		# Log status
		self.log.out('[core] STARTED.')


	def terminate(self):

		# Run only if session is still up
		if self.up:

			# Log status
			self.log.out('[core] TERMINATING ...')

			# Tell server via message to terminate
			self.client.terminate()

			# Destruct interpreter session
			self.interpreter_session.terminate()

			# Destruct Wine session, quit wine processes
			self.wineserver_session.terminate()

			# Log status
			self.log.out('[core] TERMINATED.')

			# Terminate log
			self.log.terminate()

			# Session down
			self.up = False


	def load_library(self, dll_name, dll_type = 'windll'):

		# Get full path of dll TODO
		full_path_dll = os.path.join(self.dir_cwd, dll_name)

		# Log status
		self.log.out('[core] Trying to access DLL "%s" ...' % full_path_dll)

		# Check if dll file exists
		if not os.path.isfile(full_path_dll):

			# Log status
			self.log.out('[core] ... file does NOT exist!')

			raise # TODO

		# Log status
		self.log.out('[core] ... exists ...')

		# Simplify full path
		full_path_dll = os.path.abspath(full_path_dll)

		# Check whether dll has yet not been touched
		if full_path_dll not in self.dll_dict.keys():

			# Log status
			self.log.out('[core] ... not yet touched ...')

			# Fire up new dll object
			self.dll_dict[full_path_dll] = dll_client_class(
				full_path_dll, dll_name, dll_type, self
				)

			# Log status
			self.log.out('[core] ... touched and added to list.')

		else:

			# Log status
			self.log.out('[core] ... already touched and in list.')

		# Return reference on existing dll object
		return self.dll_dict[full_path_dll]


	def __start_ctypes_client__(self):

		# Log status
		self.log.out('[core] ctypes client connecting ...')

		# Status variable
		ctypes_server_up = False
		# Time-step
		wait_for_seconds = 0.01
		# Timeout
		timeout_after_seconds = 30.0
		# Already waited for ...
		started_waiting_at = time.time()
		# Connection trys
		tried_this_many_times = 0

		# Run loop until socket appears
		while True:

			# Try to get server status
			try:

				# Count attempts
				tried_this_many_times += 1

				# Fire up xmlrpc client
				self.client = mp_client_class(
					('localhost', self.p['port_socket_ctypes']),
					'zugbruecke_server_main'
					)

				# Get status from server
				server_status = self.client.get_status()

				# Check result
				if server_status == 'up':
					ctypes_server_up = True
					break

			except:

				pass

			# Break the loop after timeout
			if time.time() >= (started_waiting_at + timeout_after_seconds):
				break

			# Wait before trying again
			time.sleep(wait_for_seconds)

		# Evaluate the result
		if not ctypes_server_up:

			# Log status
			self.log.out('[core] ... could not connect (after %0.2f seconds & %d attempts)! Error.' %
				(time.time() - started_waiting_at, tried_this_many_times)
				)
			raise # TODO

		else:

			# Log status
			self.log.out('[core] ... connected (after %0.2f seconds & %d attempts).' %
				(time.time() - started_waiting_at, tried_this_many_times)
				)


	def __prepare_python_command__(self):

		# Get socket for ctypes bridge
		self.p['port_socket_ctypes'] = get_free_port()

		# Prepare command with minimal meta info. All other info can be passed via sockets.
		self.p['command_dict'] = [
			'%s\\_server_.py' % self.wineserver_session.translate_path_unix2win(
				os.path.abspath(os.path.join(get_location_of_file(__file__), os.pardir))
				),
			'--id', self.id,
			'--port_socket_ctypes', str(self.p['port_socket_ctypes']),
			'--port_socket_log_main', str(self.p['port_socket_log_main']),
			'--log_level', str(self.p['log_level'])
			]
