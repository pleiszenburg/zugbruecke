# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/dll_client.py: Classes relevant for managing the access to DLLs

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

import ctypes
from pprint import pformat as pf

from .routine_client import routine_client_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class dll_client_class(): # Representing one idividual dll to be called into, returned by LoadLibrary


	def __init__(self, full_path_dll, dll_name, dll_type, parent_session):

		# Store dll parameters name, path and type
		self.full_path = full_path_dll
		self.name = dll_name
		self.calling_convention = dll_type

		# Store pointer to zugbruecke session
		self.session = parent_session

		# For convenience ...
		self.client = self.session.client

		# Get handle on log
		self.log = self.session.log

		# Start dict for dll routines
		self.routines = {}

		# Translate dll's full path into wine path
		self.full_path_wine = self.session.wineserver_session.translate_path_unix2win(self.full_path)

		# Status log
		self.log.out('[dll-client] New DLL file "%s" with calling convention "%s" located at' % (
			self.name, self.calling_convention
			))
		self.log.out('[dll-client]  %s' % self.full_path_wine)

		# Tell wine about the dll and its type TODO implement some sort of find_library
		result = self.client.access_dll(
			self.full_path_wine, self.full_path, self.name, self.calling_convention
			)

		# Raise error if last step failed
		if result == 0:
			raise # TODO


	def __getattr__(self, name): # Handle requests for functions in dll which have yet not been touched

		# Status log
		self.log.out('[dll-client] Trying to attach to routine "%s" in DLL file "%s" ...' % (name, self.name))

		# Is routine unknown?
		if name not in self.routines.keys():

			# Create new instance of routine_client
			self.routines[name] = routine_client_class(self, name)

		# Log status
		self.log.out('[dll-client] ... return handler for "%s" in DLL file "%s".' % (name, self.name))

		# Return handler
		return self.routines[name].handle_call
