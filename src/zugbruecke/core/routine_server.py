# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/routine_server.py: Classes for managing routines in DLLs

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

from pprint import pformat as pf
import traceback

from .arg_contents import arg_contents_class
from .arg_definition import arg_definition_class
from .arg_memory import arg_memory_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_server_class(
	arg_contents_class,
	arg_definition_class,
	arg_memory_class
	):


	def __init__(self, parent_dll, routine_name, routine_handler):

		# Store handle on parent dll
		self.dll = parent_dll

		# Store pointer to zugbruecke session
		self.session = self.dll.session

		# Get handle on log
		self.log = self.dll.log

		# Store my own name
		self.name = routine_name

		# Set routine handler
		self.handler = routine_handler


	def __handle_call__(self, arg_message_list, arg_memory_list):
		"""
		TODO: Optimize for speed!
		"""

		# Log status
		self.log.out('[routine-server] Trying call routine "%s" ...' % self.name)

		# Unpack passed arguments, handle pointers and structs ...
		args_list = self.arg_list_unpack(arg_message_list, self.argtypes_d)

		# Unpack pointer data
		memory_handle = self.server_unpack_memory_list(args_list, arg_memory_list, self.memsync_d)

		# Default return value
		return_value = None

		# This is risky
		try:

			# Call into dll
			return_value = self.handler(*tuple(args_list))

			# Pack memory for return
			arg_memory_list = self.server_pack_memory_list(memory_handle)

			# Get new arg message list
			arg_message_list = self.arg_list_pack(args_list, self.argtypes_d)

			# Log status
			self.log.out('[routine-server] ... done.')

			# Pack return package and return it
			return {
				'args': arg_message_list,
				'return_value': return_value, # TODO allow & handle pointers
				'memory': arg_memory_list,
				'success': True
				}

		except:

			# Log status
			self.log.out('[routine-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			# Pack return package and return it
			return {
				'args': arg_message_list,
				'return_value': return_value, # TODO allow & handle pointers
				'memory': arg_memory_list,
				'success': False
				}


	def __configure__(self, argtypes_d, restype_d, memsync_d):

		# Store memory sync instructions
		self.memsync_d = memsync_d

		# Store argtype definition dict
		self.argtypes_d = argtypes_d

		# Parse and apply argtype definition dict to actual ctypes routine
		self.handler.argtypes = self.unpack_definition_argtypes(argtypes_d)

		# Store return value definition dict
		self.restype_d = restype_d

		# Parse and apply restype definition dict to actual ctypes routine
		self.handler.restype = self.unpack_definition_returntype(restype_d)

		# Log status
		self.log.out(' memsync: \n%s' % pf(self.memsync_d))
		self.log.out(' argtypes: \n%s' % pf(self.handler.argtypes))
		self.log.out(' argtypes_d: \n%s' % pf(self.argtypes_d))
		self.log.out(' restype: \n%s' % pf(self.handler.restype))
		self.log.out(' restype_d: \n%s' % pf(self.restype_d))
