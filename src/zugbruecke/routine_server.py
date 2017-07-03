# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/routine_server.py: Classes relevant for managing routines in DLLs

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
import traceback

from const import (
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_ARRAY,
	GROUP_STRUCT
	)
from memory import (
	generate_pointer_from_int_list,
	serialize_pointer_into_int_list
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL SERVER CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_server_class():


	def __init__(self, parent_dll, routine_name):

		# Store handle on parent dll
		self.dll = parent_dll

		# Store pointer to zugbruecke session
		self.session = self.dll.session

		# Get handle on log
		self.log = self.dll.log

		# Store my own name
		self.name = routine_name

		# Prepare dict for custom datatypes (structs)
		self.datatypes_dict = {}

		# Log status
		self.log.out('[routine-server] Attaching to routine "%s" in DLL file "%s" ...' % (self.name, self.dll.name))

		try:

			# Get handler on routine in dll
			self.handler = getattr(
				self.dll.handler, routine_name
				)

			# Log status
			self.log.out('[routine-server] ... done.')

		except:

			# Log status
			self.log.out('[routine-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

			raise # TODO


	def call_routine(self, arg_message_list, arg_memory_list):
		"""
		TODO: Optimize for speed!
		"""

		# Log status
		self.log.out('[routine-server] Trying call routine "%s" ...' % self.name)

		# Unpack passed arguments, handle pointers and structs ...
		args, kw = self.__unpack_arguments__(arg_message_list)

		# Unpack pointer data
		memory_transport_handle = self.__unpack_memory__(args, kw, arg_memory_list)

		# Default return value
		return_value = None

		# This is risky
		try:

			# Call into dll
			return_value = self.handler(*tuple(args), **kw)

			# Log status
			self.log.out('[routine-server] ... done.')

		except:

			# Log status
			self.log.out('[routine-server] ... failed!')

			# Push traceback to log
			self.log.err(traceback.format_exc())

		# Pack memory for return
		return_memory_list = self.__pack_memory__(memory_transport_handle)

		# Pack return package and return it
		return self.__pack_return__(args, kw, return_value, return_memory_list)


	def __pack_memory__(self, memory_handle):

		# Generate new list for arrays of ints to be shipped back to the client
		memory_list = []

		# Iterate through pointers and serialize them
		for pointer in memory_handle:
			memory_list.append(serialize_pointer_into_int_list(*pointer))

		return memory_list


	def __pack_return__(self, args, kw, return_value, return_memory_list):
		"""
		TODO: Optimize for speed!
		"""

		# Start argument list as a list
		arguments_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = self.argtypes[arg_index]

			# Handle fundamental types by value
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# If by reference ...
				if arg_definition_dict['p']:

					# Append value from ctypes datatype (because most of their Python equivalents are immutable)
					arguments_list.append(arg.value)

				# If by value ...
				else:

					# Nothing to do ...
					arguments_list.append(None)

			# Handle everything else (structures etc)
			else:

				# HACK TODO
				arguments_list.append(None)

		return {
			'args': arguments_list,
			'kw': {}, # TODO not yet handled
			'return_value': return_value, # TODO allow & handle pointers
			'memory': return_memory_list
			}


	def register_argtype_and_restype(self, argtypes, restype, memsync):

		# Log status
		self.log.out('[routine-server] Set argument and return value types for "%s" ...' % self.name)

		# Store memory sync instructions
		self.memsync = memsync

		# Parse & store argtype dicts into argtypes
		self.argtypes = argtypes
		self.handler.argtypes = [self.__unpack_type_dict__(arg_dict) for arg_dict in self.argtypes]

		# Parse & store return value type
		self.restype = restype
		self.handler.restype = self.__unpack_type_dict__(self.restype)

		# Log status
		self.log.out('[routine-server] ... memsync: %s ...' % pf(self.memsync))
		self.log.out('[routine-server] ... argtypes: %s ...' % pf(self.handler.argtypes))
		self.log.out('[routine-server] ... restype: %s ...' % pf(self.handler.restype))

		# Log status
		self.log.out('[routine-server] ... done.')

		return True # Success


	def __unpack_arguments__(self, args_list):
		"""
		TODO Optimize for speed!
		"""

		# Start argument list as a list (will become a tuple)
		arguments_list = []

		# Step through arguments
		for arg_index, arg in enumerate(args_list):

			# Fetch definition of current argument
			arg_definition_dict = self.argtypes[arg_index]

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# By reference
				if arg_definition_dict['p']:

					# Put value back into its ctypes datatype
					arguments_list.append(
						getattr(ctypes, arg_definition_dict['t'])(arg[1])
						)

				# By value
				else:

					# Append value
					arguments_list.append(arg[1])

			# Handle structs
			elif arg_definition_dict['g'] == GROUP_STRUCT:

				# Generate new instance of struct datatype
				struct_arg = self.datatypes_dict[arg_definition_dict['t']]()

				# Unpack values into struct
				self.__unpack_arguments_struct__(arg_definition_dict['_fields_'], struct_arg, arg[1])

				# Append struct to list
				arguments_list.append(struct_arg)

			# Handle everything else ...
			else:

				# HACK TODO
				arguments_list.append(0)

		# Return args as tuple and kw as dict
		return arguments_list, {} # TODO kw not yet handled


	def __unpack_arguments_struct__(self, arg_definition_list, struct_inst, args_list):
		"""
		TODO Optimize for speed!
		Can be called recursively!
		"""

		# Step through arguments
		for arg_index, arg in enumerate(args_list):

			# Get current argument definition
			arg_definition_dict = arg_definition_list[arg_index]

			# Handle fundamental types
			if arg_definition_dict['g'] == GROUP_FUNDAMENTAL:

				# By reference
				if arg_definition_dict['p']:

					# Put value back into its ctypes datatype
					setattr(
						struct_inst, # struct instance to be modified
						arg[0], # parameter name (from tuple)
						getattr(ctypes, arg_definition_dict['t'])(arg[1]) # ctypes instance of type with value from tuple
						)

				# By value
				else:

					# Append value
					setattr(
						struct_inst, # struct instance to be modified
						arg[0], # parameter name (from tuple)
						arg[1] # value from tuple
						)

			# Handle structs
			elif arg_definition_dict['g'] == GROUP_STRUCT:

				# Generate new instance of struct datatype
				struct_arg = self.datatypes_dict[arg_definition_dict['t']]()

				# Unpack values into struct
				self.__unpack_arguments_struct__(arg_definition_dict['_fields'], struct_arg, arg[1])

				# Append struct to struct TODO handle pointer to structs!
				setattr(
					struct_inst, # struct instance to be modified
					arg[0], # parameter name (from tuple)
					struct_arg # value from tuple
					)

			# Handle everything else ...
			else:

				# HACK TODO
				setattr(
					struct_inst, # struct instance to be modified
					arg[0], # parameter name (from tuple)
					0 # least destructive value ...
					)


	def __unpack_memory__(self, args, kw, arg_memory_list): # TODO kw is not handled

		# Generate temporary handle for faster packing
		memory_handle = []

		# Iterate over memory segments, which must be kept in sync
		for segment_index, segment in enumerate(self.memsync):

			# Reference args - search for pointer
			pointer = args
			# Step through path to pointer ...
			for path_element in segment['p'][:-1]:
				# Go deeper ...
				pointer = pointer[path_element]

			# Handle deepest instance
			pointer[segment['p'][-1]] = generate_pointer_from_int_list(arg_memory_list[segment_index])

			# Append to handle
			memory_handle.append((pointer[segment['p'][-1]], len(arg_memory_list[segment_index])))

		return memory_handle


	def __unpack_type_dict__(self, datatype_dict):
		"""
		TODO Optimize for speed!
		"""

		# Handle fundamental C datatypes (PyCSimpleType)
		if datatype_dict['g'] == GROUP_FUNDAMENTAL:

			return self.__unpack_type_fundamental_dict__(datatype_dict)

		# Structures (PyCStructType)
		elif datatype_dict['g'] == GROUP_STRUCT:

			return self.__unpack_type_struct_dict__(datatype_dict)

		# Handle generic pointers
		elif datatype_dict['g'] == GROUP_VOID:

			return ctypes.c_void_p

		# Undhandled stuff (pointers of pointers etc.) TODO
		else:

			# Push traceback to log
			self.log.err('[routine-server] ERROR: Unhandled datatype: %s' % datatype_dict['t'])

			# HACK TODO
			return ctypes.c_int


	def __unpack_type_fundamental_dict__(self, datatype_dict):

		# Return type class or type pointer
		if datatype_dict['p']:
			return ctypes.POINTER(getattr(ctypes, datatype_dict['t']))
		else:
			return getattr(ctypes, datatype_dict['t'])


	def __unpack_type_struct_dict__(self, datatype_dict):

		# Generate struct class if it does not exist yet
		if datatype_dict['t'] not in self.datatypes_dict.keys():
			self.__unpack_type_struct_dict_generator__(datatype_dict)

		# Return type class or type pointer
		if datatype_dict['p']:
			return ctypes.POINTER(self.datatypes_dict[datatype_dict['t']])
		else:
			return self.datatypes_dict[datatype_dict['t']]


	def __unpack_type_struct_dict_generator__(self, datatype_dict):

		# Prepare fields
		fields = []

		# Step through fields
		for field in datatype_dict['_fields_']:

			# Handle fundamental C datatypes (PyCSimpleType)
			if field['g'] == GROUP_FUNDAMENTAL:

				# Add tuple with name and fundamental datatype
				fields.append((
					field['n'],
					self.__unpack_type_fundamental_dict__(field)
					))

			# Structures (PyCStructType)
			elif field['g'] == GROUP_STRUCT:

				# Add tuple with name and struct datatype
				fields.append((
					field['n'], self.__unpack_struct_dict__(field)
					))

			# Undhandled stuff (pointers of pointers etc.) TODO
			else:

				# Push traceback to log
				self.log.err('[dll-server] ERROR: Unhandled datatype in struct: %s' % datatype_dict['t'])

				# HACK TODO
				fields.append((
					field['n'], ctypes.c_int
					))

		# Generate actual class
		self.datatypes_dict[datatype_dict['t']] = type(
			datatype_dict['t'], # Potenial BUG ends up in __main__ namespace, problematic
			(ctypes.Structure,),
			{'_fields_': fields}
			)

		# Log status
		self.log.out('[dll-server] Generated struct type "%s" with fields %s' % (
			datatype_dict['t'], pf(fields)
			))
