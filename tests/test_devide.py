# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	test_devide.py: Tests by reference argument passing (int pointer)

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

import pytest

from sys import platform
if True in [platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]:
	from zugbruecke import ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class sample_class:


	def __init__(self):

		self.__dll__ = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		# int divide(int, int, int *)
		self.__divide__ = self.__dll__.cookbook_divide
		self.__divide__.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
		self.__divide__.restype = ctypes.c_int


	def divide(self, x, y):

		rem = ctypes.c_int()
		quot = self.__divide__(x, y, rem)
		return quot, rem.value


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_devide():

	sample = sample_class()

	assert (5, 2) == sample.divide(42, 8)
