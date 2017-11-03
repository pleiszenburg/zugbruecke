# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/routine_client.py: Classes for managing routines in DLLs

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
from functools import partial
from pprint import pformat as pf

from .arg_contents import arg_contents_class
from .arg_definition import arg_definition_class
from .arg_memory import arg_memory_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_client_class(
	arg_contents_class,
	arg_definition_class,
	arg_memory_class
	):


	def __init__(self, parent_dll, routine_name):

		# Store handle on parent dll
		self.dll = parent_dll

		# Store pointer to zugbruecke session
		self.session = self.dll.session

		# For convenience ...
		self.client = self.dll.client

		# Get handle on log
		self.log = self.dll.log

		# Store my own name
		self.name = routine_name

		# Set call status
		self.called = False

		# Turn a bound method into a function ... HACK?
		self.handle_call = partial(self.__handle_call__)

		# By default, there is no memory to sync
		self.handle_call.memsync = []

		# By default, assume no arguments
		self.handle_call.argtypes = []

		# By default, assume c_int return value like ctypes expects
		self.handle_call.restype = ctypes.c_int

		# Get handle on server-side configure
		self.__configure_on_server__ = getattr(
			self.client, self.dll.hash_id + '_' + str(self.name) + '_configure'
			)

		# Get handle on server-side handle_call
		self.__handle_call_on_server__ = getattr(
			self.client, self.dll.hash_id + '_' + str(self.name) + '_handle_call'
			)


	def __handle_call__(self, *args):
		"""
		TODO Optimize for speed!
		"""

		# Log status
		self.log.out('[routine-client] Trying to call routine "%s" in DLL file "%s" ...' % (self.name, self.dll.name))

		# Has this routine ever been called?
		if not self.called:

			# Log status
			self.log.out('[routine-client] ... has not been called before. Configuring ...')

			# Tell wine-python about types
			self.__configure__()

			# Change status of routine - it has been called once and is therefore configured
			self.called = True

			# Log status
			self.log.out('[routine-client] ... configured. Proceeding ...')

		# Log status
		self.log.out('[routine-client] ... parameters are "%r". Packing and pushing to server ...' % (args,))

		# Handle memory
		mem_package_list, memory_transport_handle = self.client_pack_memory_list(args, self.memsync)

		# Actually call routine in DLL! TODO Handle kw ...
		return_dict = self.__handle_call_on_server__(
			self.arg_list_pack(args, self.argtypes_d), mem_package_list
			)

		# Log status
		self.log.out('[routine-client] ... received feedback from server, unpacking ...')

		# Unpack return dict (for pointers and structs)
		self.arg_list_sync(
			args,
			self.arg_list_unpack(return_dict['args'], self.argtypes_d),
			self.argtypes_d
			)

		# Unpack memory
		self.client_unpack_memory_list(return_dict['memory'], memory_transport_handle)

		# Log status
		self.log.out('[routine-client] ... unpacked, return.')

		# Return result. return_value will be None if there was not a result.
		return return_dict['return_value']


	def __configure__(self):

		# Processing argument and return value types on first call TODO proper sanity check
		if hasattr(self.handle_call, 'memsync'):
			self.memsync = self.handle_call.memsync
		if hasattr(self.handle_call, 'argtypes'):
			self.argtypes = self.handle_call.argtypes
		if hasattr(self.handle_call, 'restype'):
			self.restype = self.handle_call.restype

		# Prepare list of arguments by parsing them into list of dicts (TODO field name / kw)
		self.argtypes_d = self.pack_definition_argtypes(self.argtypes)

		# Parse return type
		self.restype_d = self.pack_definition_returntype(self.restype)

		# Fix missing ctypes in memsync
		self.client_fix_memsync_ctypes(self.memsync)

		# Reduce memsync for transfer
		self.memsync_d = self.pack_definition_memsync(self.memsync)

		# Generate handles on relevant argtype definitions for memsync, adjust definitions with void pointers
		self.memsync_handle = self.apply_memsync_to_argtypes_definition(self.memsync, self.argtypes_d)

		# Log status
		self.log.out(' memsync: \n%s' % pf(self.memsync))
		self.log.out(' argtypes: \n%s' % pf(self.argtypes))
		self.log.out(' argtypes_d: \n%s' % pf(self.argtypes_d))
		self.log.out(' restype: \n%s' % pf(self.restype))
		self.log.out(' restype_d: \n%s' % pf(self.restype_d))

		# Pass argument and return value types as strings ...
		result = self.__configure_on_server__(
			self.argtypes_d, self.restype_d, self.memsync_d
			)
