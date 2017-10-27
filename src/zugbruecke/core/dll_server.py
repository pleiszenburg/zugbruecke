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

import traceback

from .lib import get_hash_of_string
from .routine_server import routine_server_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dll_server_class(): # Representing one idividual dll to be called into


	def __init__(self, parent_session, dll_name, dll_type, handler):

		# Store dll parameters name, path and type
		self.name = dll_name
		self.calling_convention = dll_type

		# Store pointer to _server_ session
		self.session = parent_session

		# Get handle on log
		self.log = self.session.log

		# Store handler on dll
		self.handler = handler

		# Start dict for dll routines
		self.routines = {}

		# Hash my own path as unique ID
		self.hash_id = get_hash_of_string(self.name)

		# Export registration of my functions directly
		self.session.server.register_function(
			self.__get_repr__,
			self.hash_id + '_repr'
			)
		self.session.server.register_function(
			self.__register_routine__,
			self.hash_id + '_register_routine'
			)


	def __get_repr__(self):

		return self.handler.__repr__()


	def __register_routine__(self, routine_name):
		"""
		Exposed interface
		"""

		# Just in case this routine is already known
		if routine_name in self.routines.keys():
			return True # Success

		# Log status
		self.log.out('[dll-server] Trying to access "%s" in DLL file "%s" ...' % (str(routine_name), self.name))

		# Try to attach to routine with ctypes
		try:

			# If name is a string
			if isinstance(routine_name, str):

				# Get handler on routine in dll as attribute
				routine_handler = getattr(
					self.handler, routine_name
					)

			# If name is an integer
			else:

				# Get handler on routine in dll as item
				routine_handler = self.handler[routine_name]

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
			self.hash_id + '_' + str(routine_name) + '_handle_call'
			)
		self.session.server.register_function(
			self.routines[routine_name].__configure__,
			self.hash_id + '_' + str(routine_name) + '_configure'
			)

		# Log status
		self.log.out('[dll-server] ... done.')

		return True # Success
