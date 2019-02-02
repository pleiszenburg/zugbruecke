# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/session_server.py: Handling session on Wine side

	Required to run on platform / side: [WINE]

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

import ctypes
import time
import traceback

from .data import data_class
from .dll_server import dll_server_class
from .log import log_class
from .path import path_class
from .rpc import (
	mp_client_safe_connect,
	mp_server_class
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_server_class:


	def __init__(self, session_id, parameter):

		# Store session id and parameter
		self.id = session_id
		self.p = parameter

		# Connect to Unix side
		self.rpc_client = mp_client_safe_connect(
			('localhost', self.p['port_socket_unix']),
			'zugbruecke_unix'
			)

		# Start logging session and connect it with log on unix side
		self.log = log_class(self.id, self.p, rpc_client = self.rpc_client)

		# Status log
		self.log.out('[session-server] STARTING ...')

		# Mark session as up
		self.up = True

		# Offer methods for converting paths
		path = path_class()
		self.path_unix_to_wine = path.unix_to_wine
		self.path_wine_to_unix = path.wine_to_unix

		# Start dict for dll files and routines
		self.dll_dict = {}

		# Organize all DLL types
		self.dll_types = {
			'cdll': ctypes.CDLL,
			'windll': ctypes.WinDLL,
			'oledll': ctypes.OleDLL
			}

		# Set data cache and parser
		self.data = data_class(self.log, is_server = True, callback_client = self.rpc_client)

		# Create server
		self.rpc_server = mp_server_class(
			('localhost', self.p['port_socket_wine']),
			'zugbruecke_wine',
			log = self.log,
			terminate_function = self.__terminate__
			)

		# Register call: Accessing a dll
		self.rpc_server.register_function(self.__load_library__, 'load_library')
		# Expose routine for updating parameters
		self.rpc_server.register_function(self.__set_parameter__, 'set_parameter')
		# Register destructur: Call goes into xmlrpc-server first, which then terminates parent
		self.rpc_server.register_function(self.rpc_server.terminate, 'terminate')
		# Convert path: Unix to Wine
		self.rpc_server.register_function(self.path_unix_to_wine, 'path_unix_to_wine')
		# Convert path: Wine to Unix
		self.rpc_server.register_function(self.path_wine_to_unix, 'path_wine_to_unix')

		# Expose ctypes stuff
		self.__expose_ctypes_routines__()

		# Status log
		self.log.out('[session-server] ctypes server is listening on port %d.' % self.p['port_socket_wine'])
		self.log.out('[session-server] STARTED.')
		self.log.out('[session-server] Serve forever ...')

		# Run server ...
		self.rpc_server.server_forever_in_thread(daemon = False)

		# Indicate to session client that the server is up
		self.rpc_client.set_server_status(True)


	def __expose_ctypes_routines__(self):

		# As-is exported platform-specific routines from ctypes
		for routine in [
			'FormatError',
			'get_last_error',
			'GetLastError',
			'WinError',
			'set_last_error'
			]:

			self.rpc_server.register_function(getattr(ctypes, routine), 'ctypes_' + routine)


	def __load_library__(self, dll_name, dll_type, dll_param):
		"""
		Exposed interface
		"""

		# Although this should happen only once per dll, lets be on the safe side
		if dll_name in self.dll_dict.keys():
			return (True, self.dll_dict[dll_name].hash_id) # Success & dll hash_id

		# Status log
		self.log.out('[session-server] Attaching to DLL file "%s" with calling convention "%s" ...' % (
			dll_name, dll_type
			))

		try:

			# Attach to DLL with ctypes
			handler = self.dll_types[dll_type](
				dll_name, mode = dll_param['mode'], handle = None,
				use_errno = dll_param['use_errno'],
				use_last_error = dll_param['use_last_error']
				)

		except OSError as e:

			# Log status
			self.log.out('[session-server] ... failed!')

			# Reraise error
			raise e

		except:

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise # TODO

		# Load library
		self.dll_dict[dll_name] = dll_server_class(
			self, dll_name, dll_type, handler
			)

		# Log status
		self.log.out('[session-server] ... attached.')

		# Return success and dll's hash id
		return self.dll_dict[dll_name].hash_id


	def __set_parameter__(self, parameter):

		self.p.update(parameter)


	def __terminate__(self):
		"""
		Exposed interface
		"""

		# Run only if session still up
		if self.up:

			# Status log
			self.log.out('[session-server] TERMINATING ...')

			# Terminate log
			self.log.terminate()

			# Session down
			self.up = False

			# Status log
			self.log.out('[session-server] TERMINATED.')

			# Indicate to session client that server was terminated
			self.rpc_client.set_server_status(False)
