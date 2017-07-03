# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/routine_client.py: Classes relevant for managing routines in DLLs

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

from .lib import (
	reduce_dict
	)
from .memory import (
	serialize_pointer_into_int_list
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# DLL CLIENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class routine_client_class():


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

			# Processing argument and return value types on first call
			self.__set_argtype_and_restype__()

			# Tell wine-python about types
			self.__push_argtype_and_restype__()

			# Change status of routine - it has been called once and is therefore configured
			self.called = True

			# Log status
			self.log.out('[routine-client] ... configured. Proceeding ...')

		# Log status
		self.log.out('[routine-client] ... parameters are %r / %r. Packing and pushing to server ...' % (args, kw))

		# Actually call routine in DLL! TODO Handle kw ...
		return_dict = self.client.call_dll_routine(
			self.dll.full_path, self.name, self.__pack_args__(self.argtypes_p, args), self.__pack_memory__(args)
			)

		# Log status
		self.log.out('[routine-client] ... received feedback from server, unpacking ...')

		# Unpack return dict (for pointers and structs)
		self.__unpack_return__(args, kw, return_dict)

		# Log status
		self.log.out('[routine-client] ... unpacked, return.')

		# Return result. return_value will be None if there was not a result.
		return return_dict['return_value']


	def __pack_datatype_dict__(self, datatype, field_name = None):

		# Pointer status
		is_pointer = False
		# Struct status
		is_struct = False

		try:
			# Get name of datatype
			type_name = datatype.__name__
		except:
			# Not all datatypes have a name, let's handle that
			type_name = None

		# Get group of datatype
		group_name = type(datatype).__name__ # 'PyCSimpleType', 'PyCStructType' or 'PyCPointerType'

		# Check for pointer, if yes, flag it and isolate datatype
		if group_name == 'PyCPointerType':

			is_pointer = True
			type_name = datatype._type_.__name__
			group_name = type(datatype._type_).__name__

		# Fundamental C types
		if group_name == 'PyCSimpleType':

			return {
				'n': field_name, # kw
				'p': is_pointer, # Is a pointer
				't': type_name, # Type name, such as 'c_int'
				'f': True, # Is a fundamental type (PyCSimpleType)
				's': False # Is not a struct
				}

		# Structs
		elif group_name == 'PyCStructType':

			# Get fields
			if is_pointer:
				struct_fields = datatype._type_._fields_
			else:
				struct_fields = datatype._fields_

			return {
				'n': field_name, # kw
				'p': is_pointer, # Is a pointer
				't': type_name, # Type name, such as 'c_int'
				'f': False, # Is a fundamental type (PyCSimpleType)
				's': True, # Is not a struct
				'_fields_': [
					self.__pack_datatype_dict__(field[1], field[0]) for field in struct_fields
					]
				}

		# Pointers of pointers
		elif group_name == 'PyCPointerType':

			self.log.err('[routine-client] ERROR: Unhandled pointer of pointer')
			raise # TODO

		# UNKNOWN stuff, likely pointers - handled without datatype
		else:

			return {
				'n': field_name, # kw
				'p': True, # Is a pointer
				't': type_name, # Type name, such as 'c_int'
				'f': False, # Is not a fundamental type (PyCSimpleType)
				's': False # Is not a struct
				}


	def __pack_args__(self, argtypes_p_sub, args): # TODO kw
		"""
		TODO Optimize for speed!
		"""

		# Shortcut for speed
		arguments_list = []

		# Step through arguments
		for arg_index, arg_definition_dict in enumerate(argtypes_p_sub):

			# Fetch current argument
			if type(args) is list or type(args) is tuple:
				arg = args[arg_index]
			else:
				arg = getattr(args, arg_definition_dict['n'])

			# Handle fundamental types
			if arg_definition_dict['f']:

				# If pointer
				if arg_definition_dict['p']:

					try:

						# Append value from ctypes datatype (because most of their Python equivalents are immutable)
						arguments_list.append((arg_definition_dict['n'], arg.value))

					except:

						# HACK Append value from ctypes datatype pointer ...
						arguments_list.append((arg_definition_dict['n'], arg.contents.value))

				# If value
				else:

					# Append value
					arguments_list.append((arg_definition_dict['n'], arg))

			# Handle structs
			elif arg_definition_dict['s']:

				# Reclusively call this routine for packing structs
				arguments_list.append((arg_definition_dict['n'], self.__pack_args__(
					arg_definition_dict['_fields_'], arg
					)))

			# Handle everything else (structures)
			else:

				# HACK TODO
				arguments_list.append(None)

		# Return parameter message list - MUST WORK WITH PICKLE
		return arguments_list


	def __pack_memory__(self, args):

		# Start empty package
		mem_package_list = []

		# Iterate over memory segments, which must be kept in sync
		for segment_index, segment in enumerate(self.memsync):

			# Reference args - search for pointer
			pointer = args
			# Step through path to pointer ...
			for path_element in segment['p']:
				# Go deeper ...
				pointer = pointer[path_element]

			# Reference args - search for length
			length = args
			# Step through path to pointer ...
			for path_element in segment['l']:
				# Go deeper ...
				length = length[path_element]

			# Defaut type, of nothing is given, is unsigned byte
			if '_t' not in segment.keys():
				segment['_t'] = ctypes.c_ubyte

			# Compute actual length - might come from ctypes or a Python datatype
			try:
				length_value = length.value * ctypes.sizeof(segment['_t'])
			except:
				length_value = length * ctypes.sizeof(segment['_t'])

			# Convert argument into ctypes datatype TODO more checks needed!
			if '_c' in segment.keys():
				arg_value = ctypes.pointer(segment['_c'].from_param(pointer))
			else:
				arg_value = pointer

			# Serialize the data ...
			data = serialize_pointer_into_int_list(arg_value, length_value)

			# Append data to package
			mem_package_list.append(data)

		# TODO remove
		self.log.out(pf(mem_package_list))

		return mem_package_list


	def __process_memsync__(self, memsync, argtypes_p):

		# Reduce memsync so it can be forwarded to server
		memsync_p = [reduce_dict(sync_element) for sync_element in memsync]

		# Start empty handle list
		memsync_handle = []

		# Iterate over memory segments, which must be kept in sync
		for segment in memsync:

			# Reference processed argument types - start with depth 0
			arg_type = argtypes_p[segment['p'][0]]
			# Step through path to argument type ...
			for path_element in segment['p'][1:]:
				# Go deeper ...
				arg_type = arg_type['_fields_'][path_element]

			# Reference processed argument types - start with depth 0
			len_type = argtypes_p[segment['l'][0]]
			# Step through path to argument type ...
			for path_element in segment['l'][1:]:
				# Go deeper ...
				len_type = len_type['_fields_'][path_element]

			# Add to list
			memsync_handle.append({
				'p': arg_type,
				'l': len_type
				})

		return memsync_p, memsync_handle


	def __push_argtype_and_restype__(self):

		# Prepare list of arguments by parsing them into list of dicts (TODO field name / kw)
		self.argtypes_p = [self.__pack_datatype_dict__(arg) for arg in self.argtypes]

		# Parse return type
		self.restype_p = self.__pack_datatype_dict__(self.restype)

		# Reduce memsync
		self.memsync_p, self.memsync_handle = self.__process_memsync__(self.memsync, self.argtypes_p)

		# Pass argument and return value types as strings ...
		result = self.client.register_argtype_and_restype(
			self.dll.full_path, self.name, self.argtypes_p, self.restype_p, self.memsync_p
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


	def __set_argtype_and_restype__(self):

		# TODO proper sanity check
		try:
			self.memsync = self.handle_call.memsync
		except:
			pass
		try:
			self.argtypes = self.handle_call.argtypes
		except:
			pass
		try:
			self.restype = self.handle_call.restype
		except:
			pass

		# Log status
		self.log.out('[routine-client]  memsync: %s' % pf(self.memsync))
		self.log.out('[routine-client]  argtypes: %s' % pf(self.argtypes))
		self.log.out('[routine-client]  restype: %s' % pf(self.restype))


	def __unpack_return__(self, args, kw, return_dict): # TODO kw not yet handled
		"""
		TODO Optimize for speed!
		"""

		# Get arguments' list
		arguments_list = return_dict['args']

		# Step through arguments
		for arg_index, arg in enumerate(args):

			# Fetch definition of current argument
			arg_definition_dict = self.argtypes_p[arg_index]

			# Handle fundamental types
			if arg_definition_dict['f']:

				# If by reference ...
				if arg_definition_dict['p']:

					# Put value back into its ctypes datatype
					args[arg_index].value = arguments_list[arg_index]

				# If by value
				else:

					# Nothing to do
					pass

			# Handle everything else (structures and "the other stuff")
			else:

				# HACK TODO
				pass
