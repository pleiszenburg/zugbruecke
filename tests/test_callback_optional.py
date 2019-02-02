# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_callback_optional.py: Optional callback routines as arguments

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
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class_a:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		conveyor_belt = ctypes.WINFUNCTYPE(ctypes.c_int16, ctypes.c_int16)

		self.__use_optional_callback__ = self.__dll__.use_optional_callback_a
		self.__use_optional_callback__.argtypes = (ctypes.c_int16, conveyor_belt)
		self.__use_optional_callback__.restype = ctypes.c_int16

		@conveyor_belt
		def process_data(in_data):
			return in_data ** 2

		self.__process_data__ = process_data


	def use_optional_callback(self, some_data):

		return self.__use_optional_callback__(some_data, self.__process_data__)


class sample_class_b:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		self.__use_optional_callback__ = self.__dll__.use_optional_callback_b
		self.__use_optional_callback__.argtypes = (ctypes.c_int16, ctypes.c_void_p)
		self.__use_optional_callback__.restype = ctypes.c_int16


	def do_not_use_optional_callback(self, some_data):

		return self.__use_optional_callback__(some_data, None)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_use_optional_callback():

	sample = sample_class_a()

	assert 18 == sample.use_optional_callback(3)


def test_do_not_use_optional_callback():

	sample = sample_class_b()

	assert 14 == sample.do_not_use_optional_callback(7)
