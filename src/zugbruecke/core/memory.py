# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/memory.py: Handles memory transfers between both sides

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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def generate_pointer_from_int_list(int_array):

	return ctypes.pointer((ctypes.c_ubyte * len(int_array))(*int_array))


def overwrite_pointer_with_int_list(ctypes_pointer, int_array):

	(ctypes.c_ubyte * len(int_array)).from_address(ctypes.c_void_p.from_buffer(ctypes_pointer).value)[:] = int_array[:]


def serialize_pointer_into_int_list(ctypes_pointer, size_bytes):

	return (ctypes.c_ubyte * size_bytes).from_address(ctypes.c_void_p.from_buffer(ctypes_pointer).value)[:]
