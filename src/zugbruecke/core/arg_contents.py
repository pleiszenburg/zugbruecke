# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/arg_contents.py: (Un-) packing of argument contents

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
from pprint import pformat as pf
import traceback

from .const import (
	FLAG_POINTER,
	GROUP_VOID,
	GROUP_FUNDAMENTAL,
	GROUP_STRUCT
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class arg_contents_class():


	def arg_list_pack(self, args_tuple, argtypes_list):

		# Return parameter message list - MUST WORK WITH PICKLE
		return [(d['n'], self.__pack_item__(a, d)) for a, d in zip(args_tuple, argtypes_list)]


	def arg_list_unpack(self, args_package_list, argtypes_list):

		# Return args as list, will be converted into tuple on call
		return [self.__unpack_item__(a[1], d) for a, d in zip(args_package_list, argtypes_list)]


	def arg_list_sync(self, old_arguments_list, new_arguments_list, argtypes_list):

		# Step through arguments
		for old_arg, new_arg, arg_def_dict in zip(
			old_arguments_list, new_arguments_list, argtypes_list
			):
			self.__sync_item__(
				old_arg, new_arg, arg_def_dict
				)


	def __item_pointer_strip__(self, arg_in):

		# Handle pointer object
		if hasattr(arg_in, 'contents'):
			return arg_in.contents
		# Handle reference (byref) 'light pointer'
		elif hasattr(arg_in, '_obj'):
			return arg_in._obj
		# Object was likely not provided as a pointer
		else:
			return arg_in


	def __item_value_strip__(self, arg_in):

		if hasattr(arg_in, 'value'):
			return arg_in.value
		else:
			return arg_in


	def __pack_item__(self, arg_in, arg_def_dict):

		# Grep the simple case first, scalars
		if arg_def_dict['s']:

			# Strip away the pointers ... (all flags are pointers in this case)
			for flag in arg_def_dict['f']:
				if flag != FLAG_POINTER:
					raise # TODO
				arg_in = self.__item_pointer_strip__(arg_in)

			# Handle fundamental types
			if arg_def_dict['g'] == GROUP_FUNDAMENTAL:
				# Append argument to list ...
				return self.__item_value_strip__(arg_in)
			# Handle structs
			elif arg_def_dict['g'] == GROUP_STRUCT:
				# Reclusively call this routine for packing structs
				return self.__pack_item_struct__(arg_in, arg_def_dict)
			# Handle everything else ... likely pointers handled by memsync
			else:
				# Just return None - will (hopefully) be overwritten by memsync
				return None

		# The non-trivial case, involving arrays
		else:

			return self.__pack_item_array__(arg_in, arg_def_dict)


	def __pack_item_array__(self, arg_in, arg_def_dict, flag_index_start = 0):

		for flag_index in range(flag_index_start, len(arg_def_dict['f'])):

			# Extract the flag
			flag = arg_def_dict['f'][flag_index]

			# Handle pointers
			if flag == FLAG_POINTER:

				arg_in = self.__item_pointer_strip__(arg_in)

			# Handle arrays
			elif flag > 0:

				# Only dive deeper if this is not the last flag
				if flag_index < len(arg_def_dict['f']) - 1:
					arg_in = [
						self.__pack_item_array__(
							e, arg_def_dict, flag_index_start = flag_index + 1
							) for e in arg_in[:]
						]
				else:
					arg_in = arg_in[:]
					if arg_def_dict['g'] == GROUP_STRUCT:
						arg_in = [
							self.__pack_item_struct__(e, arg_def_dict) for e in arg_in
							]

			# Handle unknown flags
			else:

				raise # TODO

		return arg_in


	def __pack_item_struct__(self, struct_raw, struct_def_dict):

		# Return parameter message list - MUST WORK WITH PICKLE
		return [(field_def_dict['n'], self.__pack_item__(
				getattr(struct_raw, field_def_dict['n']), field_def_dict
				)) for field_def_dict in struct_def_dict['_fields_']]


	def __sync_item__(self, old_arg, new_arg, arg_def_dict):

		# Grep the simple case first, scalars
		if arg_def_dict['s']:

			# Strip away the pointers ... (all flags are pointers in this case)
			for flag in arg_def_dict['f']:
				if flag != FLAG_POINTER:
					raise # TODO
				old_arg = self.__item_pointer_strip__(old_arg)
				new_arg = self.__item_pointer_strip__(new_arg)

			if arg_def_dict['g'] == GROUP_FUNDAMENTAL:
				if hasattr(old_arg, 'value'):
					old_arg.value = new_arg.value
				else:
					pass # only relevant within structs or for actual pointers to scalars
			elif arg_def_dict['g'] == GROUP_STRUCT:
				return self.__sync_item_struct__(old_arg, new_arg, arg_def_dict)
			else:
				pass # DO NOTHING?

		# The non-trivial case, arrays
		elif not arg_def_dict['s']:

			self.__sync_item_array__(old_arg, new_arg, arg_def_dict)


	def __sync_item_array__(self, old_arg, new_arg, arg_def_dict, flag_index_start = 0):

		for flag_index in range(flag_index_start, len(arg_def_dict['f'])):

			# Extract the flag
			flag = arg_def_dict['f'][flag_index]

			# Handle pointers
			if flag == FLAG_POINTER:

				old_arg = self.__item_pointer_strip__(old_arg)
				new_arg = self.__item_pointer_strip__(new_arg)

			# Handle arrays
			elif flag > 0:

				# Only dive deeper if this is not the last flag
				if flag_index < len(arg_def_dict['f']) - 1:

					for old_arg_e, new_arg_e in zip(old_arg[:], new_arg[:]):
						self.__sync_item_array__(
							old_arg_e, new_arg_e, arg_def_dict,
							flag_index_start = flag_index + 1
							)

				else:

					if arg_def_dict['g'] == GROUP_FUNDAMENTAL:
						old_arg[:] = new_arg[:]
					elif arg_def_dict['g'] == GROUP_STRUCT:
						for old_struct, new_struct in zip(old_arg[:], new_arg[:]):
							self.__sync_item_struct__(old_struct, new_struct, arg_def_dict)
					else:
						raise # TODO

			# Handle unknown flags
			else:

				raise # TODO


	def __sync_item_struct__(self, old_struct, new_struct, struct_def_dict):

		# Step through arguments
		for field_def_dict in struct_def_dict['_fields_']:

			self.__sync_item__(
				getattr(old_struct, field_def_dict['n']),
				getattr(new_struct, field_def_dict['n']),
				field_def_dict
				)


	def __unpack_item__(self, arg_raw, arg_def_dict):

		# Again the simple case first, scalars of any kind
		if arg_def_dict['s']:

			# Handle fundamental types
			if arg_def_dict['g'] == GROUP_FUNDAMENTAL:
				arg_rebuilt = getattr(ctypes, arg_def_dict['t'])(arg_raw)
			# Handle structs
			elif arg_def_dict['g'] == GROUP_STRUCT:
				arg_rebuilt = self.__unpack_item_struct__(arg_raw, arg_def_dict)
			# Handle voids (likely mensync stuff)
			elif arg_def_dict['g'] == GROUP_VOID:
				# Return a placeholder
				return None
			# Handle everything else ...
			else:
				raise # TODO

			# Step through flags in reverse order (if it's not a memsync field)
			for flag in reversed(arg_def_dict['f']):
				if flag != FLAG_POINTER:
					raise # TODO
				arg_rebuilt = ctypes.pointer(arg_rebuilt)

			return arg_rebuilt

		# And now arrays ...
		else:

			return self.__unpack_item_array__(arg_raw, arg_def_dict)[1]


	def __unpack_item_array__(self, arg_in, arg_def_dict, flag_index = 0):

		# Extract the flag
		flag = arg_def_dict['f'][flag_index]

		# Dive deeper?
		if flag_index < len(arg_def_dict['f']) - 1:

			# Get index of next flag
			next_flag_index = flag_index + 1

			# If it's a Python list, dive once per element of list
			if type(arg_in) == list and flag != FLAG_POINTER:

				arg_in_tuple_list = [self.__unpack_item_array__(
					e, arg_def_dict, flag_index = next_flag_index
					) for e in arg_in]
				arg_type = arg_in_tuple_list[0][0]
				arg_in = [e[1] for e in arg_in_tuple_list]

			# Likely a scalar or a ctypes object
			else:

				arg_type, arg_in = self.__unpack_item_array__(
					arg_in, arg_def_dict, flag_index = next_flag_index
					)

			# Handle pointers
			if flag == FLAG_POINTER:
				arg_type = ctypes.POINTER(arg_type)
				arg_in = ctypes.pointer(arg_in)
			# Handle arrays
			elif flag > 0:
				arg_type = arg_type * flag
				arg_in = arg_type(*arg_in)
			# Handle unknown flags
			else:
				raise # TODO

		# No dive, we're at the bottom - just get the original ctypes type
		else:

			if flag == FLAG_POINTER:
				raise # TODO

			if arg_def_dict['g'] == GROUP_FUNDAMENTAL:
				arg_type = getattr(ctypes, arg_def_dict['t']) * flag
				arg_in = arg_type(*arg_in)
			elif arg_def_dict['g'] == GROUP_STRUCT:
				arg_type = self.struct_type_dict[arg_def_dict['t']] * flag
				arg_in = arg_type(*(self.__unpack_item_struct__(e, arg_def_dict) for e in arg_in))
			else:
				raise # TODO

		return arg_type, arg_in


	def __unpack_item_struct__(self, args_list, struct_def_dict):

		# Generate new instance of struct datatype
		struct_inst = self.struct_type_dict[struct_def_dict['t']]()

		# Step through arguments
		for field_def_dict, field_arg in zip(struct_def_dict['_fields_'], args_list):

			setattr(
				struct_inst, # struct instance to be modified
				field_arg[0], # parameter name (from tuple)
				self.__unpack_item__(field_arg[1], field_def_dict) # parameter value
				)

		return struct_inst
