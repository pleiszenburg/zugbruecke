# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/data/memory.py: Handles memory transfers between both sides

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

def generate_pointer_from_bytes(in_bytes):

	return ctypes.cast(ctypes.pointer((ctypes.c_ubyte * len(in_bytes)).from_buffer_copy(in_bytes)), ctypes.c_void_p)


def overwrite_pointer_with_bytes(ctypes_pointer, in_bytes):

	ctypes.memmove(ctypes_pointer, ctypes.pointer((ctypes.c_ubyte * len(in_bytes)).from_buffer_copy(in_bytes)), len(in_bytes))


def serialize_pointer_into_bytes(ctypes_pointer, size_bytes):

	return bytes(ctypes.cast(ctypes_pointer, ctypes.POINTER(ctypes.c_ubyte * size_bytes)).contents)


def is_null_pointer(ctypes_pointer):

	try:
		return ctypes.cast(ctypes_pointer, ctypes.c_void_p).value is None
	except ctypes.ArgumentError: # catch non-pointer arguments
		return False
