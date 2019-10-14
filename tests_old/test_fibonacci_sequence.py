# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_fibonacci_sequence.py: Test allocation of memory by DLL, returned as struct

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
	import zugbruecke.ctypes as ctypes
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

		self.__fibonacci_sequence__ = self.__dll__.fibonacci_sequence_a
		self.__fibonacci_sequence__.argtypes = (ctypes.c_int16,)
		self.__fibonacci_sequence__.restype = ctypes.POINTER(int_array_data)
		self.__fibonacci_sequence__.memsync = [
			{
				'p': ['r', 'data'],
				'l': ['r', 'len'],
				't': 'c_int16'
				}
			]


	def fibonacci_sequence(self, length):

		out_array_obj = self.__fibonacci_sequence__(length)

		return ctypes.cast(
			out_array_obj.contents.data,
			ctypes.POINTER(ctypes.c_int16 * length)
			).contents[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_fibonacci_sequence():

	sample = sample_class()

	assert [1, 1, 2, 3, 5, 8, 13, 21, 34, 55] == sample.fibonacci_sequence(10)
