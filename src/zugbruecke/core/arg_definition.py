# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/arg_definition.py: (Un-) packing of argument definitions

	Required to run on platform / side: [UNIX, WINE]

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
#from pprint import pformat as pf

from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)
from .lib import (
	reduce_dict
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Definition packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class arg_definition_class():


	struct_type_dict = {}


	def apply_memsync_to_argtypes_definition(self, memsync, argtypes_d):

		# Start empty handle list
		memsync_handle = []

		# Iterate over memory segments, which must be kept in sync
		for segment in memsync:

			# Reference processed argument types - start with depth 0
			arg_type = argtypes_d[segment['p'][0]]
			# Step through path to argument type ...
			for path_element in segment['p'][1:]:
				# Go deeper ...
				arg_type = arg_type['_fields_'][path_element]

			# Reference processed argument types - start with depth 0
			len_type = argtypes_d[segment['l'][0]]
			# Step through path to argument type ...
			for path_element in segment['l'][1:]:
				# Go deeper ...
				len_type = len_type['_fields_'][path_element]

			# HACK make memory sync pointers type agnostic
			arg_type['g'] = GROUP_VOID
			arg_type['t'] = None # no type string

			# Add to list
			memsync_handle.append({
				'p': arg_type, # Handle on pointer argument definition
				'l': len_type # Handle on length argument definition
				})

		return memsync_handle


	def pack_definition_argtypes(self, argtypes):

		return [self.__pack_definition_dict__(arg) for arg in argtypes]


	def pack_definition_memsync(self, memsync):

		return [reduce_dict(sync_element) for sync_element in memsync]


	def pack_definition_returntype(self, restype):

		return self.__pack_definition_dict__(restype)


	def unpack_definition_argtypes(self, argtypes_d):

		return [self.__unpack_definition_dict__(arg_d_dict) for arg_d_dict in argtypes_d]


	def unpack_definition_returntype(self, restype_d):

		return self.__unpack_definition_dict__(restype_d)


	def __generate_struct_from_definition__(self, struct_d_dict):

		# Prepare fields
		fields = []

		# Step through fields
		for field in struct_d_dict['_fields_']:

			# Handle fundamental C datatypes (PyCSimpleType)
			if field['g'] == GROUP_FUNDAMENTAL:

				# Add tuple with name and fundamental datatype
				fields.append((
					field['n'],
					self.__unpack_definition_fundamental_dict__(field)
					))

			# Structures (PyCStructType)
			elif field['g'] == GROUP_STRUCT:

				# Add tuple with name and struct datatype
				fields.append((
					field['n'], self.__unpack_definition_struct_dict__(field)
					))

			# Undhandled stuff (pointers of pointers etc.) TODO
			else:

				# HACK TODO
				fields.append((
					field['n'], ctypes.c_int
					))

		# Generate actual class
		self.struct_type_dict[struct_d_dict['t']] = type(
			struct_d_dict['t'], # Potenial BUG: Ends up in __main__ scope, problematic?
			(ctypes.Structure,),
			{'_fields_': fields}
			)


	def __pack_definition_dict__(self, datatype, field_name = None):

		# Not all datatypes have a name, let's handle that
		type_name = None
		# Get name of datatype, such as c_int, if there is one
		if hasattr(datatype, '__name__'):
			type_name = datatype.__name__

		# Get group of datatype
		group_name = type(datatype).__name__
		# Can be: 'PyCSimpleType', 'PyCStructType', PyCArrayType or 'PyCPointerType'

		# List of flags: Pointer flag or length of array (one entry per dimension)
		flag_list = []

		# Strip away all pointers and arrays until simple type or struct type is left & keep order
		while group_name in ['PyCPointerType', 'PyCArrayType']:

			# Catch pointer
			if group_name == 'PyCPointerType':

				# Append pointer flag to list of flags
				flag_list.append(FLAG_POINTER)

			# Catch arrays
			elif group_name == 'PyCArrayType':

				# Append length to flag list
				flag_list.append(datatype._length_)

			# This is not supposed to happen ...
			else:

				raise

			# Get next type in sequence
			datatype = datatype._type_

			# Get type and group name of next type in sequence
			type_name = datatype.__name__
			group_name = type(datatype).__name__

		# Store the depth of arrays (arrays within arrays etc; for speed)
		flag_array_depth = len([flag for flag in flag_list if flag > 0])

		# Flag pure scalars as, well, pure scalars (for speed)
		flag_scalar = flag_array_depth == 0

		# Flag elements containing pointers
		flag_pointer = len([flag for flag in flag_list if flag == FLAG_POINTER]) != 0

		# Fundamental ('simple') C types
		if group_name == 'PyCSimpleType':

			return {
				'f': flag_list,
				's': flag_scalar,
				'd': flag_array_depth,
				'p': flag_pointer,
				'n': field_name, # kw
				't': type_name, # Type name, such as 'c_int'
				'g': GROUP_FUNDAMENTAL
				}

		# Structs
		elif group_name == 'PyCStructType':

			# Keep track of datatype on client side
			if type_name not in self.struct_type_dict.keys():
				self.struct_type_dict[type_name] = datatype

			return {
				'f': flag_list,
				's': flag_scalar,
				'd': flag_array_depth,
				'p': flag_pointer,
				'n': field_name, # kw
				't': type_name, # Type name, such as 'c_int'
				'g': GROUP_STRUCT,
				'_fields_': [
					self.__pack_definition_dict__(field[1], field[0]) for field in datatype._fields_
					]
				}

		# UNKNOWN stuff, likely pointers - handled without datatype
		else:

			return {
				'f': flag_list,
				's': flag_scalar,
				'd': flag_array_depth,
				'p': flag_pointer,
				'n': field_name, # kw
				't': type_name, # Type name, such as 'c_int'
				'g': GROUP_VOID # Let's try void
				}


	def __unpack_definition_dict__(self, datatype_d_dict):

		# Handle fundamental C datatypes (PyCSimpleType)
		if datatype_d_dict['g'] == GROUP_FUNDAMENTAL:

			return self.__unpack_definition_fundamental_dict__(datatype_d_dict)

		# Structures (PyCStructType)
		elif datatype_d_dict['g'] == GROUP_STRUCT:

			return self.__unpack_definition_struct_dict__(datatype_d_dict)

		# Handle generic pointers
		elif datatype_d_dict['g'] == GROUP_VOID:

			return self.__unpack_definition_flags__(
				ctypes.c_void_p,
				datatype_d_dict['f'],
				is_void_pointer = True
				)

		# Undhandled stuff (pointers of pointers etc.) TODO
		else:

			# HACK TODO
			return self.__unpack_definition_flags__(
				ctypes.c_int, # HACK let's assume int
				datatype_d_dict['f'] # flags
				)


	def __unpack_definition_flags__(self, datatype, flag_list, is_void_pointer = False):

		# Re-create arrays and pointers
		for flag_index, flag in enumerate(reversed(flag_list)):
			if flag > 0: # array
				datatype = datatype * flag
			elif flag == FLAG_POINTER:
				if not is_void_pointer: # do this only for last flag TODO
					datatype = ctypes.POINTER(datatype)
			else:
				raise # TODO

		return datatype


	def __unpack_definition_fundamental_dict__(self, datatype_d_dict):

		# Return type class or type pointer
		return self.__unpack_definition_flags__(
			getattr(ctypes, datatype_d_dict['t']),
			datatype_d_dict['f'],
			datatype_d_dict['t'] is 'c_void_p'
			)


	def __unpack_definition_struct_dict__(self, datatype_d_dict):

		# Generate struct class if it does not exist yet
		if datatype_d_dict['t'] not in self.struct_type_dict.keys():
			self.__generate_struct_from_definition__(datatype_d_dict)

		# Return type class or type pointer
		return self.__unpack_definition_flags__(
			self.struct_type_dict[datatype_d_dict['t']], # struct class
			datatype_d_dict['f'] # flags
			)
