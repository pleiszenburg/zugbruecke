# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/session_server.py: Handling session on Wine side

	Required to run on platform / side: [WINE]

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

import ctypes
import traceback

from .dll_server import dll_server_class
from .log import log_class
from .path import path_class
from .rpc import mp_server_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_server_class:


	def __init__(self, session_id, parameter):

		# Store session id and parameter
		self.id = session_id
		self.p = parameter

		# Start logging session and connect it with log on unix side
		self.log = log_class(self.id, self.p)

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

		# Create server
		self.server = mp_server_class(
			('localhost', self.p['port_socket_ctypes']),
			'zugbruecke_server_main',
			log = self.log,
			terminate_function = self.__terminate__
			)

		# Return status of server
		self.server.register_function(self.__get_status__, 'get_status')
		# Register call: Accessing a dll
		self.server.register_function(self.__load_library__, 'load_library')
		# Expose routine for updating parameters
		self.server.register_function(self.__set_parameter__, 'set_parameter')
		# Register destructur: Call goes into xmlrpc-server first, which then terminates parent
		self.server.register_function(self.server.terminate, 'terminate')
		# Convert path: Unix to Wine
		self.server.register_function(self.path_unix_to_wine, 'path_unix_to_wine')
		# Convert path: Wine to Unix
		self.server.register_function(self.path_wine_to_unix, 'path_wine_to_unix')

		# Expose ctypes stuff
		self.__expose_ctypes_routines__()

		# Status log
		self.log.out('[session-server] ctypes server is listening on port %d.' % self.p['port_socket_ctypes'])
		self.log.out('[session-server] STARTED.')
		self.log.out('[session-server] Serve forever ...')

		# Run server ...
		self.server.serve_forever()


	def __expose_ctypes_routines__(self):

		# As-is exported platform-specific routines from ctypes
		for routine in [
			'FormatError',
			'get_last_error',
			'GetLastError',
			'WinError',
			'set_last_error'
			]:

			self.server.register_function(getattr(ctypes, routine), 'ctypes_' + routine)


	def __get_status__(self):
		"""
		Exposed interface
		"""

		if self.up:
			return 'up'
		else:
			return 'down'


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

			# Load library
			self.dll_dict[dll_name] = dll_server_class(
				self, dll_name, dll_type, handler
				)

			# Log status
			self.log.out('[session-server] ... done.')

			# Return success and dll's hash id
			return (True, self.dll_dict[dll_name].hash_id) # Success

		except:

			# Log status
			self.log.out('[session-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			return (False, None) # Fail


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

			# Status log
			self.log.out('[session-server] TERMINATED.')

			# Session down
			self.up = False
