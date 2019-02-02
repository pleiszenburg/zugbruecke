# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_square_int_array_with_struct.py: Test allocation of memory by DLL in struct

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

import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class int_array_data(ctypes.Structure):


	_fields_ = [
		('data', ctypes.POINTER(ctypes.c_int16)),
		('len', ctypes.c_int16)
		]


class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__square_int_array_with_struct__ = self.__dll__.square_int_array_with_struct
		self.__square_int_array_with_struct__.argtypes = (
			ctypes.POINTER(int_array_data),
			ctypes.POINTER(int_array_data)
			)
		self.__square_int_array_with_struct__.memsync = [
			{
				'p': [0, 'data'],
				'l': [0, 'len'],
				't': 'c_int16'
				},
			{
				'p': [1, 'data'],
				'l': [1, 'len'],
				't': 'c_int16'
				}
			]


	def square_int_array_with_struct(self, in_array):

		in_array_obj = int_array_data()
		out_array_obj = int_array_data()

		in_array_obj.data = ctypes.cast(
			ctypes.pointer((ctypes.c_int16 * len(in_array))(*in_array)),
			ctypes.POINTER(ctypes.c_int16)
			)
		in_array_obj.len = len(in_array)

		self.__square_int_array_with_struct__(
			in_array_obj,
			out_array_obj
			)

		return ctypes.cast(
			out_array_obj.data,
			ctypes.POINTER(ctypes.c_int16 * len(in_array))
			).contents[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_square_int_array_with_struct():

	sample = sample_class()

	assert [4, 16, 9, 25] == sample.square_int_array_with_struct([2, 4, 3, 5])
