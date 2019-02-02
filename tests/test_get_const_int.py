# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_sqrt_int.py: Test function call without parameters

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
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_sqrt_int():

		dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		get_const_int = dll.get_const_int
		get_const_int.restype = ctypes.c_int16

		assert 7 == get_const_int()


def test_sqrt_int_with_tuple():

		dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		get_const_int = dll.get_const_int
		get_const_int.argtypes = tuple()
		get_const_int.restype = ctypes.c_int16

		assert 7 == get_const_int()


def test_sqrt_int_with_list():

		dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')

		get_const_int = dll.get_const_int
		get_const_int.argtypes = []
		get_const_int.restype = ctypes.c_int16

		assert 7 == get_const_int()
