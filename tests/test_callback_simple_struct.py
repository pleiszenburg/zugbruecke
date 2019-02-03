# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_callback_simple_struct.py: Demonstrates callback in struct

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

# import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

conveyor_belt = ctypes.WINFUNCTYPE(ctypes.c_int16, ctypes.c_int16)


class conveyor_belt_data(ctypes.Structure):


	_fields_ = [
		('len', ctypes.c_int16),
		('get_data', conveyor_belt)
		]


class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__sum_elements_from_callback_in_struct__ = self.__dll__.sum_elements_from_callback_in_struct
		self.__sum_elements_from_callback_in_struct__.argtypes = (ctypes.POINTER(conveyor_belt_data),)
		self.__sum_elements_from_callback_in_struct__.restype = ctypes.c_int16

		self.DATA = [1, 6, 8, 4, 9, 7, 4, 2, 5, 2]

		@conveyor_belt
		def get_data(index):
			print((index, self.DATA[index]))
			return self.DATA[index]

		self.__get_data__ = get_data


	def sum_elements_from_callback_in_struct(self):

		in_struct = conveyor_belt_data(len(self.DATA), self.__get_data__)

		return self.__sum_elements_from_callback_in_struct__(in_struct)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_callback_simple():

	sample = sample_class()

	assert 48 == sample.sum_elements_from_callback_in_struct()
