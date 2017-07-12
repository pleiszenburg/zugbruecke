# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/arg_memory.py: (Un-) packing of argument pointers

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
from .memory import (
	overwrite_pointer_with_int_list,
	serialize_pointer_into_int_list
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class arg_memory_class():


	def pack_memory(self, args, memsync):

		# Start empty package for transfer
		mem_package_list = []

		# Store pointers locally so their memory can eventually be overwritten
		memory_handle = []

		# Iterate over memory segments, which must be kept in sync
		for segment_index, segment in enumerate(memsync):

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

			# Compute actual length - might come from ctypes or a Python datatype
			if hasattr(length, 'value'):
				length_value = length.value * ctypes.sizeof(segment['_t'])
			else:
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

			# Append actual pointer to handler list
			memory_handle.append(arg_value)

		return mem_package_list, memory_handle


	def unpack_memory(self, mem_package_list, memory_handle):

		# Overwrite the local pointers with new data
		for pointer_index, pointer in enumerate(memory_handle):
			overwrite_pointer_with_int_list(pointer, mem_package_list[pointer_index])
