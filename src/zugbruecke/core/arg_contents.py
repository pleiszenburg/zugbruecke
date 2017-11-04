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

		if hasattr(arg_in, 'contents'):
			return arg_in.contents
		else:
			return arg_in


	def __item_value_strip__(self, arg_in):

		if hasattr(arg_in, 'value'):
			return arg_in.value
		else:
			return arg_in


	def __pack_item__(self, arg_in, arg_def_dict, flag_index_start = 0):

		for flag_index in range(flag_index_start, len(arg_def_dict['f'])): # step through flags

			# Extract the flag
			flag = arg_def_dict['f'][flag_index]

			# Handle pointers
			if flag == FLAG_POINTER:
				arg_in = self.__item_pointer_strip__(arg_in)

			# Handle arrays
			elif flag > 0:
				arg_in = self.__pack_item_array__(
					arg_in, arg_def_dict,
					flag_index_start = flag_index + 1
					)

			# Handle unknown flags
			else:
				raise # TODO

		return self.__pack_item_content__(arg_in, arg_def_dict)


	def __pack_item_array__(self, arg_in, arg_def_dict, flag_index_start = 0):

		arg_in = arg_in[:]

		return arg_in


	def __pack_item_content__(self, arg_in, arg_def_dict):

		# Handle fundamental types
		if arg_def_dict['g'] == GROUP_FUNDAMENTAL:

			# Append argument to list ...
			return self.__pack_item_fundamental__(arg_in, arg_def_dict)

		# Handle structs
		elif arg_def_dict['g'] == GROUP_STRUCT:

			# Reclusively call this routine for packing structs
			return self.__pack_item_struct__(arg_in, arg_def_dict)

		# Handle everything else ... likely pointers handled by memsync
		else:

			# Just return None - will (hopefully) be overwritten by memsync
			return None


	def __pack_item_fundamental__(self, arg_raw, arg_def_dict):

		return self.__item_value_strip__(arg_raw)


	def __pack_item_struct__(self, struct_raw, struct_def_dict):

		# Return parameter message list - MUST WORK WITH PICKLE
		return [(field_def_dict['n'], self.__pack_item__(
				getattr(struct_raw, field_def_dict['n']), field_def_dict
				)) for field_def_dict in struct_def_dict['_fields_']]


	def __sync_item__(self, old_arg, new_arg, arg_def_dict):

		# Handle fundamental types
		if arg_def_dict['g'] == GROUP_FUNDAMENTAL:

			# HACK let's handle pointers to scalars like before
			if len(arg_def_dict['f']) == 1 and arg_def_dict['f'][0] == FLAG_POINTER:

				old_arg_ref = self.__item_pointer_strip__(old_arg)
				new_arg_value = self.__item_value_strip__(self.__item_pointer_strip__(new_arg))
				if hasattr(old_arg_ref, 'value'):
					old_arg_ref.value = new_arg_value
				else:
					old_arg_ref = new_arg_value

			# HACK let's handle 1D fixed length arrays
			elif len(arg_def_dict['f']) == 2 and arg_def_dict['f'][0] == FLAG_POINTER and arg_def_dict['f'][1] > 0:

				self.__item_pointer_strip__(old_arg)[:] = self.__item_pointer_strip__(new_arg)[:]

		else:

			pass # TODO struct ...


	def __unpack_item__(self, arg_raw, arg_def_dict):

		# Handle fundamental types
		if arg_def_dict['g'] == GROUP_FUNDAMENTAL:

			return self.__unpack_item_fundamental__(arg_raw, arg_def_dict)

		# Handle structs
		elif arg_def_dict['g'] == GROUP_STRUCT:

			return self.__unpack_item_struct__(arg_raw, arg_def_dict)

		# Handle voids (likely mensync stuff)
		elif arg_def_dict['g'] == GROUP_VOID:

			# Return a placeholder
			return 0

		# Handle everything else ...
		else:

			# HACK TODO
			self.log.err('__unpack_item__ NEITHER STRUCT NOR FUNDAMENTAL?')
			self.log.err(str(arg_def_dict['g']))
			return None


	def __unpack_item_fundamental__(self, arg_rebuilt, arg_def_dict):

		# Handle scalars, whether pointer or not
		if arg_def_dict['s']:
			arg_rebuilt = getattr(ctypes, arg_def_dict['t'])(arg_rebuilt)

		# Step through flags in reverse order
		for flag in reversed(arg_def_dict['f']):

			if flag == FLAG_POINTER:

				arg_rebuilt = ctypes.pointer(arg_rebuilt)

			elif flag > 0:

				# TODO does not really handle arrays of arrays (yet)
				arg_rebuilt = (flag * getattr(ctypes, arg_def_dict['t']))(*arg_rebuilt)

			else:

				raise

		return arg_rebuilt


	def __unpack_item_struct__(self, args_list, struct_def_dict):

		# Generate new instance of struct datatype
		struct_inst = self.struct_type_dict[struct_def_dict['t']]()

		# Fetch fields for speed
		struct_fields = struct_def_dict['_fields_']

		# Step through arguments
		for arg_index, arg in enumerate(args_list):

			setattr(
				struct_inst, # struct instance to be modified
				arg[0], # parameter name (from tuple)
				self.__unpack_item__(arg[1], struct_fields[arg_index]) # parameter value
				)

		return struct_inst
