# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/dll_server.py: Classes for managing the access to DLLs

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
from pprint import pformat as pf

from .lib import get_hash_of_string
from .routine_server import routine_server_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dll_server_class(): # Representing one idividual dll to be called into


	def __init__(self, full_path_dll, full_path_dll_unix, dll_name, dll_type, parent_session):

		# Store dll parameters name, path and type
		self.full_path = full_path_dll
		self.full_path_unix = full_path_dll_unix
		self.name = dll_name
		self.calling_convention = dll_type

		# Store pointer to _server_ session
		self.session = parent_session

		# Get handle on log
		self.log = self.session.log

		# Start dict for dll routines
		self.routines = {}

		# Status log
		self.log.out('[dll-server] Attaching to DLL file "%s" with calling convention "%s" located at' % (
			self.name, self.calling_convention
			))
		self.log.out('[dll-server]  %s' % self.full_path)

		try:

			# Attach to DLL with ctypes
			self.handler = ctypes.windll.LoadLibrary(self.full_path) # TODO handle oledll and cdll

			# Hash my own path as unique ID
			self.hash_id = get_hash_of_string(self.full_path_unix)

			# Export registration of my functions directly
			self.session.server.register_function(
				self.register_routine,
				self.hash_id + '_register_routine'
				)

			# Log status
			self.log.out('[dll-server] ... done.')

		except:

			# Log status
			self.log.out('[dll-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise


	def register_routine(self, routine_name):

		# Just in case this routine is already known
		if routine_name in self.routines.keys():
			return True # Success

		# Log status
		self.log.out('[dll-server] Trying to access "%s" in DLL file "%s" ...' % (routine_name, self.name))

		# Try to attach to routine with ctypes
		try:

			# Get handler on routine in dll
			routine_handler = getattr(
				self.handler, routine_name
				)

		except:

			# Log status
			self.log.out('[dll-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			return False # Fail

		# Generate new instance of routine class
		self.routines[routine_name] = routine_server_class(self, routine_name, routine_handler)

		# Export call and configration directly
		self.session.server.register_function(
			self.routines[routine_name].__handle_call__,
			self.hash_id + '_' + routine_name + '_handle_call'
			)
		self.session.server.register_function(
			self.routines[routine_name].__configure__,
			self.hash_id + '_' + routine_name + '_configure'
			)

		# Log status
		self.log.out('[dll-server] ... done.')

		return True # Success
