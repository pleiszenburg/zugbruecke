# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/core.py: Core classes for managing pycrosscall sessions

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

import atexit
import os
import signal
import time

from .config import get_module_config
from .dll import dll_session_class
from .interpreter import interpreter_session_class
from .lib import (
	get_location_of_file,
	setup_wine_python
	)
from .log import log_class
from .wineserver import wineserver_session_class
from .rpc import (
	xmlrpc_client
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PYCROSSCALL SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_class():


	def __init__(self, parameter = {}):

		# Fill empty parameters with default values
		self.p = get_module_config(parameter)

		# Get and set session id
		self.id = self.p['id']

		# Start session logging
		self.log = log_class(self.id, self.p)

		# Extract server port from log module
		self.p['port_server_log'] = self.log.server_port

		# Log status
		self.log.out('[core] STARTING ...')
		self.log.out('[core] Configured Wine-Python version is %s for %s.' % (self.p['version'], self.p['arch']))
		self.log.out('[core] Log server is listening on port %d.' % self.p['port_server_log'])

		# Store current working directory
		self.dir_cwd = os.getcwd()

		# Install wine-python
		setup_wine_python(self.p['arch'], self.p['version'], self.p['dir'])

		# Initialize Wine session
		self.wineserver_session = wineserver_session_class(self.id, self.p, self.log)

		# Log status
		self.log.out('[core] Mode: "%s".' % self.p['mode'])

		# Prepare python command for ctypes server or interpreter
		self.__prepare_python_command__()

		# Initialize interpreter session
		self.interpreter_session = interpreter_session_class(self.id, self.p, self.log, self.wineserver_session)

		# If in ctypes mode ...
		self.__prepare_ctypes__()

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

			# If in ctypes mode ...
			if self.p['mode'] == 'ctypes':

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


	def __loadlibrary__(self, dll_name, dll_type = 'windll'):

		# Get full path of dll
		full_path_dll = os.path.join(self.dir_cwd, dll_name)

		# Log status
		self.log.out('[core] Trying to access DLL "%s" ...' % full_path_dll)

		# Check if dll file exists
		if not os.path.isfile(full_path_dll):

			# Log status
			self.log.out('[core] ... does NOT exist!')

			raise # TODO

		# Log status
		self.log.out('[core] ... exists ...')

		# Simplyfy full path
		full_path_dll = os.path.abspath(full_path_dll)

		# Check whether dll has yet not been touched
		if full_path_dll not in self.dll_dict.keys():

			# Log status
			self.log.out('[core] ... not yet touched ...')

			# Fire up new dll object
			self.dll_dict[full_path_dll] = dll_session_class(
				full_path_dll, dll_name, dll_type, self
				)

			# Log status
			self.log.out('[core] ... touched and added to list.')

		else:

			# Log status
			self.log.out('[core] ... already touched and in list.')

		# Return reference on existing dll object
		return self.dll_dict[full_path_dll]


	def __prepare_ctypes__(self):

		# Allow only in ctypes mode
		if self.p['mode'] == 'ctypes':

			# Set up a dict for loaded dlls
			self.dll_dict = {}

			# Expose LoadLibrary
			self.LoadLibrary = self.__loadlibrary__

			# HACK Wait ... becomes obsolete, when client is moved. Client needs retries and a timeout
			time.sleep(1) # seconds

			# Fire up xmlrpc client
			self.client = xmlrpc_client(('localhost', 8000))

			# Log status
			self.log.out('[core] XML-RPX-client started.')


	def __prepare_python_command__(self):

		# If in ctypes mode, prepare command
		if self.p['mode'] == 'ctypes':

			# Prepare command
			self.p['command_dict'] = [
				'%s\\_server_.py' % self.wineserver_session.translate_path_unix2win(get_location_of_file(__file__)),
				'--id', self.id,
				'--port_in', str(self.p['port_wine']),
				'--port_server_log', str(self.p['port_server_log']),
				'--log_level', str(self.p['log_level'])
				]

		# If in interpreter mode, parse parameters and prepare command
		elif self.p['mode'] == 'interpreter':

			# Empty command starts interpreter TODO parse cmd line
			self.p['command_dict'] = []

		else:

			# Log status
			self.log.out('[core] Error: Unkown mode!')

			# Unknown mode
			raise # TODO


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINDLL CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class windll_class(): # Mimic ctypes.windll


	def __init__(self):

		# Session not yet up
		self.up = False


	def start_session(self, parameter = {}):

		# Session not yet up?
		if not self.up:

			# Fire up a new session
			self.__session__ = session_class(parameter)

			# Mark session as up
			self.up = True


	def LoadLibrary(self, name):

		# Session not yet up?
		if not self.up:

			# Fire up session
			self.start_session()

		# Return a DLL instance object from within the session
		return self.__session__.LoadLibrary(dll_name = name, dll_type = 'windll')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# STAND-ALONE PYTHON INTERPRETER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class python_interpreter():


	def __init__(self, cmd_line_args):

		print('!!!')


	def start_session(self, parameter = {}):

		# Set session mode to ctypes bridge
		# parameter['mode'] = 'interpreter'
		# Start normal session here

		pass


	def run(self):

		pass
