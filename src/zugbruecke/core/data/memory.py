# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/data/memory.py: (Un-) packing of argument pointers

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2018 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
#import traceback

from ..memory import (
	generate_pointer_from_bytes,
	overwrite_pointer_with_bytes,
	serialize_pointer_into_bytes
	)

WCHAR_BYTES = ctypes.sizeof(ctypes.c_wchar)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Memory content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class memory_class():


	def client_fix_memsync_ctypes(self, memsync_d_list):

		# Iterate over memory segments, which must be kept in sync
		for memsync_d in memsync_d_list:

			# Defaut type, if nothing is given, is unsigned byte
			if '_t' not in memsync_d.keys():
				memsync_d['_t'] = ctypes.c_ubyte

			# Handle Unicode - off by default
			if 'w' not in memsync_d.keys():
				memsync_d['w'] = False


	def client_pack_memory_list(self, args_tuple, memsync_d_list):

		# Pack data for every pointer, append data to package
		return [self.__pack_memory_item__(args_tuple, memsync_d) for memsync_d in memsync_d_list]


	def client_unpack_memory_list(self, mem_package_list, memsync_d_list):

		# Iterate over memory package dicts
		for memory_d, memsync_d in zip(mem_package_list, memsync_d_list):

			# Adjust Unicode wchar length
			if memsync_d['w']:
				self.__adjust_wchar_length__(memory_d)

			# Overwrite the local pointers with new data
			overwrite_pointer_with_bytes(
				ctypes.c_void_p(memory_d['_a']),
				memory_d['d']
				)


	def server_pack_memory_list(self, mem_package_list, memsync_d_list):

		# Iterate through pointers and serialize them
		for memory_d, memsync_d in zip(mem_package_list, memsync_d_list):

			# Overwrite old data in package with new data from memory
			memory_d['d'] = serialize_pointer_into_bytes(
				ctypes.c_void_p(memory_d['a']), memory_d['l']
				)


	def server_unpack_memory_list(self, args_tuple, arg_memory_list, memsync_d_list):

		# Iterate over memory segments, which must be kept in sync
		for memory_d, memsync_d in zip(arg_memory_list, memsync_d_list):

			# Unpack one memory section / item
			self.__unpack_memory_item__(args_tuple, memory_d, memsync_d)


	def __adjust_wchar_length__(self, memory_d):

		old_len = memory_d['w']
		new_len = WCHAR_BYTES

		if old_len == new_len:
			return

		tmp = bytearray(memory_d['l'] * new_len // old_len)

		for index in range(old_len if new_len > old_len else new_len):
			tmp[index::new_len] = memory_d['d'][index::old_len]

		memory_d['d'] = bytes(tmp)
		memory_d['l'] = len(memory_d['d'])
		memory_d['w'] = WCHAR_BYTES


	def __get_argument_by_memsync_path__(self, args_tuple, memsync_path):

		# Reference args_tuple as initial value
		element = args_tuple

		# Step through path
		for path_element in memsync_path:

			# Go deeper ... # TODO use __item_pointer_strip__ ?
			if isinstance(path_element, int):
				element = element[path_element]
			else:
				element = getattr(self.__item_pointer_strip__(element), path_element)

		return element


	def __pack_memory_item__(self, args_tuple, memsync_d):

		# Search for pointer
		pointer = self.__get_argument_by_memsync_path__(args_tuple, memsync_d['p'])

		# Is there a function defining the length?
		if '_f' in memsync_d.keys() and isinstance(memsync_d['l'], tuple):

			# Start list for length function arguments
			length_func_arg_list = []

			# Iterate over length components
			for length_component in memsync_d['l']:

				# Append length argument to list
				length_func_arg_list.append(self.__get_argument_by_memsync_path__(args_tuple, length_component))

			# Compute length
			length = memsync_d['_f'](*length_func_arg_list)

		else:

			# Search for length
			length = self.__get_argument_by_memsync_path__(args_tuple, memsync_d['l'])

		# Compute actual length - might come from ctypes or a Python datatype
		length_value = getattr(length, 'value', length) * ctypes.sizeof(memsync_d['_t'])

		# Convert argument into ctypes datatype TODO more checks needed!
		if '_c' in memsync_d.keys():
			arg_value = ctypes.pointer(memsync_d['_c'].from_param(pointer))
		else:
			arg_value = pointer

		# Serialize the data ...
		memory_bytes = serialize_pointer_into_bytes(arg_value, length_value)

		return {
			'd': memory_bytes, # serialized data
			'l': len(memory_bytes), # length of serialized data
			'a': ctypes.cast(arg_value, ctypes.c_void_p).value, # local pointer address as integer
			'w': WCHAR_BYTES if memsync_d['w'] else None # local length of Unicode wchar if required
			}


	def __unpack_memory_item__(self, args_tuple, memory_d, memsync_d):

		# Adjust Unicode wchar length
		if memsync_d['w']:
			self.__adjust_wchar_length__(memory_d)

		# Search for pointer in passed arguments
		pointer_arg = self.__get_argument_by_memsync_path__(args_tuple, memsync_d['p'][:-1])

		# Generate pointer to passed data
		pointer_data = generate_pointer_from_bytes(memory_d['d'])

		# Cache the client's memory address
		memory_d['_a'] = memory_d['a']

		# If we're in the top level arguments or an array ...
		if isinstance(memsync_d['p'][-1], int):
			# Handle deepest instance (exchange element in list/tuple) HACK
			pointer_arg[memsync_d['p'][-1]] = pointer_data
			# Store the server's memory address
			memory_d['a'] = ctypes.cast(pointer_arg[memsync_d['p'][-1]], ctypes.c_void_p).value
		# If we're at a field of a struct
		else:
			# Handle deepest instance
			setattr(pointer_arg.contents, memsync_d['p'][-1], pointer_data)
			# Store the server's memory address
			memory_d['a'] = pointer_data.value
