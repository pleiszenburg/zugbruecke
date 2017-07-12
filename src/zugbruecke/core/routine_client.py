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

from .arg_definition import arg_definition_class
from .arg_memory import arg_memory_class
from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_client_class(
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

		# Tell server about routine
		self.__register_routine_on_server__()


	def __handle_call__(self, *args, **kw):
		"""
		TODO Optimize for speed!
		"""

		# Log status
		self.log.out('[routine-client] Trying to call routine "%s" in DLL file "%s" ...' % (self.name, self.dll.name))

		# Has this routine ever been called?
		if not self.called:

			# Log status
			self.log.out('[routine-client] ... has not been called before. Configuring ...')

			# Processing argument and return value types on first call TODO proper sanity check
			if hasattr(self.handle_call, 'memsync'):
				self.memsync = self.handle_call.memsync
			if hasattr(self.handle_call, 'argtypes'):
				self.argtypes = self.handle_call.argtypes
			if hasattr(self.handle_call, 'restype'):
				self.restype = self.handle_call.restype

			# Log status
			self.log.out('[routine-client]  memsync: %s' % pf(self.memsync))
			self.log.out('[routine-client]  argtypes: %s' % pf(self.argtypes))
			self.log.out('[routine-client]  restype: %s' % pf(self.restype))

			# Tell wine-python about types
			self.__push_argtype_and_restype__()

			# Change status of routine - it has been called once and is therefore configured
			self.called = True

			# Log status
			self.log.out('[routine-client] ... configured. Proceeding ...')

		# Log status
		self.log.out('[routine-client] ... parameters are %r / %r. Packing and pushing to server ...' % (args, kw))

		# Handle memory
		mem_package_list, memory_transport_handle = self.client_pack_memory(args, self.memsync)

		# Actually call routine in DLL! TODO Handle kw ...
		return_dict = self.client.call_dll_routine(
			self.dll.full_path, self.name, self.__pack_args__(self.argtypes_d, args), mem_package_list
			)

		# Log status
		self.log.out('[routine-client] ... received feedback from server, unpacking ...')

		# Unpack return dict (for pointers and structs)
		self.__unpack_return__(args, kw, return_dict)

		# Unpack memory
		self.client_unpack_memory(return_dict['memory'], memory_transport_handle)

		# Log status
		self.log.out('[routine-client] ... unpacked, return.')

		# Return result. return_value will be None if there was not a result.
		return return_dict['return_value']


	def __pack_args__(self, argtypes_p_sub, args): # TODO kw
		"""
		TODO Optimize for speed!
		"""

		# Shortcut for speed
		arguments_list = []

		# Step through arguments
		for arg_index, arg_definition_dict in enumerate(argtypes_p_sub):

			# Fetch current argument by index from tuple or by name from struct/kw
			if type(args) is list or type(args) is tuple:
				arg = args[arg_index]
			else:
				arg = getattr(args, arg_definition_dict['n'])

			# TODO:
			# append tuple to list "arguments_list"
			# tuple contains: (arg_definition_dict['n'], argument content / value)
			#  pointer: arg.value or arg.contents.value
			#  (value: Append value from ctypes datatype, because most of their Python equivalents are immutable)
			#  (contents.value: Append value from ctypes datatype pointer ...)
			#  by value: just "arg"

			try:

				arg_value = arg # Set up arg for iterative unpacking
				for flag in arg_definition_dict['f']: # step through flags

					# Handle pointers
					if flag == FLAG_POINTER:

						# There are two ways of getting the actual value
						if hasattr(arg_value, 'value'):
							arg_value = arg_value.value
						elif hasattr(arg_value, 'contents'):
							arg_value = arg_value.contents
						else:
							raise # TODO

					# Handle arrays
					elif flag > 0:

						arg_value = arg_value[:]

					# Handle unknown flags
					else:

						raise # TODO
			except:

				self.log.err(pf(arg_value))

			self.log.err('   abc')
			self.log.err(pf(arg_value))

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# Append argument to list ...
				arguments_list.append((arg_definition_dict['n'], arg_value))

			# Handle structs
			elif arg_definition_dict['g'] == GROUP_STRUCT:

				# Reclusively call this routine for packing structs
				arguments_list.append((arg_definition_dict['n'], self.__pack_args__(
					arg_definition_dict['_fields_'], arg
					)))

			# Handle everything else ... likely pointers handled by memsync
			else:

				# Just return None - will (hopefully) be overwritten by memsync
				arguments_list.append(None)

		# Return parameter message list - MUST WORK WITH PICKLE
		return arguments_list


	def __push_argtype_and_restype__(self):

		# Prepare list of arguments by parsing them into list of dicts (TODO field name / kw)
		self.argtypes_d = self.pack_definition_argtypes(self.argtypes)

		# Parse return type
		self.restype_d = self.pack_definition_returntype(self.restype)

		# Fix missing ctypes in memsync
		self.fix_memsync_ctypes(self.memsync)

		# Reduce memsync for transfer
		self.memsync_d = self.pack_definition_memsync(self.memsync)

		# Generate handles on relevant argtype definitions for memsync, adjust definitions with void pointers
		self.memsync_handle = self.apply_memsync_to_argtypes_definition(self.memsync, self.argtypes_d)

		# Pass argument and return value types as strings ...
		result = self.client.register_argtype_and_restype(
			self.dll.full_path, self.name, self.argtypes_d, self.restype_d, self.memsync_d
			)

		# Handle error
		if result == 0:
			raise # TODO


	def __register_routine_on_server__(self):

		# Log status
		self.log.out('[routine-client] Registering routine "%s" on server ...' % self.name)

		# Register routine in wine
		result = self.client.register_routine(self.dll.full_path, self.name)

		# If success ...
		if result:

			# Log status
			self.log.out('[routine-client] ... done (unconfigured).')

		# If failed ...
		else:

			# Log status
			self.log.out('[routine-client] ... failed!')

			raise # TODO


	def __unpack_return__(self, args, kw, return_dict): # TODO kw not yet handled
		"""
		TODO Optimize for speed!
		"""

		# Get arguments' list
		arguments_list = return_dict['args']

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = self.argtypes_d[arg_index]

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# Start process with plain old argument
				arg_value = args[arg_index]
				# New value is: arguments_list[arg_index]

				# Step through flags
				for flag in arg_definition_dict['f']:

					# Handle pointers
					if flag == FLAG_POINTER:

						# There are two ways of getting the actual value
						# if hasattr(arg_value, 'value'):
						# 	arg_value = arg_value.value
						if hasattr(arg_value, 'contents'):
							arg_value = arg_value.contents
						else:
							arg_value = arg_value

					# Handle arrays
					elif flag > 0:

						arg_value = arg_value

					# Handle unknown flags
					else:

						raise # TODO

				if hasattr(arg_value, 'value'):
					arg_value.value = arguments_list[arg_index]
				else:
					arg_value = arguments_list[arg_index]

				# # If by reference ...
				# if arg_definition_dict['p']:
				# 	# Put value back into its ctypes datatype
				# 	args[arg_index].value = arguments_list[arg_index]
				# # If by value
				# else:
				# 	# Nothing to do
				# 	pass

			# Handle everything else (structures and "the other stuff")
			else:

				# HACK TODO
				pass
