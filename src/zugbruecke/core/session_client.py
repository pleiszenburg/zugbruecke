# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/session.py: Classes for managing zugbruecke sessions

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
from ctypes import (
	_FUNCFLAG_CDECL,
	_FUNCFLAG_USE_ERRNO,
	_FUNCFLAG_USE_LASTERROR
	)
import os
import signal
import time

from .const import _FUNCFLAG_STDCALL
from .config import get_module_config
from .data import data_class
from .dll_client import dll_client_class
from .interpreter import interpreter_session_class
from .lib import (
	get_free_port,
	get_location_of_file
	)
from .log import log_class
from .rpc import (
	mp_client_safe_connect,
	mp_server_class
	)
from .wineenv import (
	create_wine_prefix,
	setup_wine_python,
	set_wine_env
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ZUGBRUECKE SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_client_class():


	def __init__(self, parameter = {}, force = False):

		self.__init_stage_1__(parameter, force)


	def ctypes_FormatError(self, code = None):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.ctypes_FormatError(code)


	def ctypes_get_last_error(self):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.ctypes_get_last_error()


	def ctypes_GetLastError(self):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.ctypes_GetLastError()


	def ctypes_set_last_error(self, value):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.ctypes_set_last_error(value)


	def ctypes_WinError(self, code = None, descr = None):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.ctypes_WinError(code, descr)


	def ctypes_CFUNCTYPE(self, restype, *argtypes, **kw):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		flags = _FUNCFLAG_CDECL

		if kw.pop("use_errno", False):
			flags |= _FUNCFLAG_USE_ERRNO
		if kw.pop("use_last_error", False):
			flags |= _FUNCFLAG_USE_LASTERROR
		if kw:
			raise ValueError("unexpected keyword argument(s) %s" % kw.keys())

		return self.data.generate_callback_decorator(flags, restype, *argtypes)


	def ctypes_WINFUNCTYPE(self, restype, *argtypes, **kw): # EXPORT

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		flags = _FUNCFLAG_STDCALL

		if kw.pop("use_errno", False):
			flags |= _FUNCFLAG_USE_ERRNO
		if kw.pop("use_last_error", False):
			flags |= _FUNCFLAG_USE_LASTERROR
		if kw:
			raise ValueError("unexpected keyword argument(s) %s" % kw.keys())

		return self.data.generate_callback_decorator(flags, restype, *argtypes)


	def load_library(self, dll_name, dll_type, dll_param = {}):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Check whether dll has already been touched
		if dll_name in self.dll_dict.keys():

			# Return reference on existing dll object
			return self.dll_dict[dll_name]

		# Is DLL type known?
		if dll_type not in ['cdll', 'windll', 'oledll']:

			# Raise error if unknown
			raise # TODO

		# Fix parameters dict with defauls values
		if 'mode' not in dll_param.keys():
			dll_param['mode'] = 0
		if 'use_errno' not in dll_param.keys():
			dll_param['use_errno'] = False
		if 'use_last_error' not in dll_param.keys():
			dll_param['use_last_error'] = False

		# Log status
		self.log.out('[session-client] Attaching to DLL file "%s" with calling convention "%s" ...' % (dll_name, dll_type))

		try:

			# Tell wine about the dll and its type
			hash_id = self.rpc_client.load_library(
				dll_name, dll_type, dll_param
				)

		except OSError as e:

			# Log status
			self.log.out('[session-client] ... failed!')

			# If DLL was not found, reraise error
			raise e

		# Fire up new dll object
		self.dll_dict[dll_name] = dll_client_class(
			self, dll_name, dll_type, hash_id
			)

		# Log status
		self.log.out('[session-client] ... attached.')

		# Return reference on existing dll object
		return self.dll_dict[dll_name]


	def path_unix_to_wine(self, in_path):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.path_unix_to_wine(in_path)


	def path_wine_to_unix(self, in_path):

		# If in stage 1, fire up stage 2
		if self.stage == 1:
			self.__init_stage_2__()

		# Ask the server
		return self.rpc_client.path_wine_to_unix(in_path)


	def set_parameter(self, parameter):

		self.p.update(parameter)
		self.rpc_client.set_parameter(parameter)


	def terminate(self):

		# Run only if session is still up
		if self.up:

			# Log status
			self.log.out('[session-client] TERMINATING ...')

			# Only if in stage 2:
			if self.stage == 2:

				# Wait for server to appear
				self.__wait_for_server_status_change__(target_status = False)

				# Tell server via message to terminate
				self.rpc_client.terminate()

				# Destruct interpreter session
				self.interpreter_session.terminate()

			# Terminate callback server
			self.rpc_server.terminate()

			# Log status
			self.log.out('[session-client] TERMINATED.')

			# Terminate log
			self.log.terminate()

			# Session down
			self.up = False


	def __init_stage_1__(self, parameter, force_stage_2):

		# Fill empty parameters with default values and/or config file contents
		self.p = get_module_config(parameter)

		# Get and set session id
		self.id = self.p['id']

		# Start RPC server for callback routines
		self.__start_rpc_server__()

		# Start session logging
		self.log = log_class(self.id, self.p, rpc_server = self.rpc_server)

		# Log status
		self.log.out('[session-client] STARTING (STAGE 1) ...')
		self.log.out('[session-client] Configured Wine-Python version is %s for %s.' % (self.p['version'], self.p['arch']))
		self.log.out('[session-client] Log socket port: %d.' % self.p['port_socket_unix'])

		# Store current working directory
		self.dir_cwd = os.getcwd()

		# Set data cache and parser
		self.data = data_class(self.log, is_server = False, callback_server = self.rpc_server)

		# Set up a dict for loaded dlls
		self.dll_dict = {}

		# Mark session as up
		self.up = True

		# Marking server component as down
		self.server_up = False

		# Set current stage to 1
		self.stage = 1

		# Register session destructur
		atexit.register(self.terminate)
		signal.signal(signal.SIGINT, self.terminate)
		signal.signal(signal.SIGTERM, self.terminate)

		# Log status
		self.log.out('[session-client] STARTED (STAGE 1).')

		# If stage 2 shall start with force ...
		if force_stage_2:
			self.__init_stage_2__()


	def __init_stage_2__(self):

		# Log status
		self.log.out('[session-client] STARTING (STAGE 2) ...')

		# Install wine-python
		setup_wine_python(self.p['arch'], self.p['version'], self.p['dir'])

		# Initialize Wine session
		self.dir_wineprefix = set_wine_env(self.p['dir'], self.p['arch'])
		create_wine_prefix(self.dir_wineprefix)

		# Prepare python command for ctypes server or interpreter
		self.__prepare_python_command__()

		# Initialize interpreter session
		self.interpreter_session = interpreter_session_class(self.id, self.p, self.log)

		# Wait for server to appear
		self.__wait_for_server_status_change__(target_status = True)

		# Try to connect to Wine side
		self.__start_rpc_client__()

		# Set current stage to 2
		self.stage = 2

		# Log status
		self.log.out('[session-client] STARTED (STAGE 2).')


	def __set_server_status__(self, status):

		# Interface for session server through RPC
		self.server_up = status


	def __start_rpc_client__(self):

		# Fire up xmlrpc client
		self.rpc_client = mp_client_safe_connect(
			('localhost', self.p['port_socket_wine']),
			'zugbruecke_wine'
			)


	def __start_rpc_server__(self):

		# Get socket for callback bridge
		self.p['port_socket_unix'] = get_free_port()

		# Create server
		self.rpc_server = mp_server_class(
			('localhost', self.p['port_socket_unix']),
			'zugbruecke_unix'
			) # Log is added later

		# Interface to server to indicate its status
		self.rpc_server.register_function(self.__set_server_status__, 'set_server_status')

		# Start server into its own thread
		self.rpc_server.server_forever_in_thread()


	def __prepare_python_command__(self):

		# Get socket for ctypes bridge
		self.p['port_socket_wine'] = get_free_port()

		# Prepare command with minimal meta info. All other info can be passed via sockets.
		self.p['command_dict'] = [
			os.path.join(
				os.path.abspath(os.path.join(get_location_of_file(__file__), os.pardir)),
				'_server_.py'
				),
			'--id', self.id,
			'--port_socket_wine', str(self.p['port_socket_wine']),
			'--port_socket_unix', str(self.p['port_socket_unix']),
			'--log_level', str(self.p['log_level']),
			'--log_write', str(int(self.p['log_write']))
			]


	def __wait_for_server_status_change__(self, target_status):

		# Does the status have to change?
		if target_status == self.server_up:

			# No, so get out of here
			return

		# Debug strings
		STATUS_DICT = {True: 'up', False: 'down'}

		# Log status
		self.log.out('[session-client] Waiting for session-server to be %s ...' % STATUS_DICT[target_status])

		# Time-step
		wait_for_seconds = 0.01
		# Timeout
		timeout_after_seconds = 30.0
		# Already waited for ...
		started_waiting_at = time.time()

		# Run loop until socket appears
		while not self.server_up:

			# Wait before trying again
			time.sleep(wait_for_seconds)

			# Time out
			if time.time() >= (started_waiting_at + timeout_after_seconds):
				break

		# Handle timeout
		if not self.server_up:

			# Log status
			self.log.out('[session-client] ... wait timed out (after %0.2f seconds).' %
				(time.time() - started_waiting_at)
				)

			raise # TODO

		# Log status
		self.log.out('[session-client] ... session server is %s (after %0.2f seconds).' %
			(STATUS_DICT[target_status], time.time() - started_waiting_at)
			)
