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
import os
from pprint import pformat as pf
import sys
import traceback

from .dll_server import dll_server_class
from .log import log_class
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
		self.log.out('[_server_] STARTING ...')

		# Mark session as up
		self.up = True

		# Start dict for dll files and routines
		self.dll_dict = {}

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
		# Register destructur: Call goes into xmlrpc-server first, which then terminates parent
		self.server.register_function(self.server.terminate, 'terminate')

		# Status log
		self.log.out('[_server_] ctypes server is listening on port %d.' % self.p['port_socket_ctypes'])
		self.log.out('[_server_] STARTED.')
		self.log.out('[_server_] Serve forever ...')

		# Run server ...
		self.server.serve_forever()


	def __get_status__(self):
		"""
		Exposed interface
		"""

		if self.up:
			return 'up'
		else:
			return 'down'


	def __load_library__(self, full_path_dll, full_path_dll_unix, dll_name, dll_type):
		"""
		Exposed interface
		"""

		# Although this should happen only once per dll, lets be on the safe side
		if full_path_dll_unix not in self.dll_dict.keys():

			try:

				# Load library
				self.dll_dict[full_path_dll_unix] = dll_server_class(
					full_path_dll, full_path_dll_unix, dll_name, dll_type, self
					)

				# Return success and dll's hash id
				return (True, self.dll_dict[full_path_dll_unix].hash_id) # Success

			except:

				return (False, None) # Fail

		# If its already in the list, just return success
		else:

			# Just in case
			return (True, self.hash)


	def __terminate__(self):
		"""
		Exposed interface
		"""

		# Run only if session still up
		if self.up:

			# Status log
			self.log.out('[_server_] TERMINATING ...')

			# Terminate log
			self.log.terminate()

			# Status log
			self.log.out('[_server_] TERMINATED.')

			# Session down
			self.up = False
