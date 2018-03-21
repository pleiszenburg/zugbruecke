# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_error_callargs.py: Test error handling when malformed arguments are passed

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

import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke as ctypes
elif platform.startswith('win'):
	import ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def test_error_callargs_unconfigured_too_many_args():

	dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')
	square_int = dll.square_int

	with pytest.raises(ValueError):
		a = square_int(1, 2, 3)


def test_error_callargs_unconfigured_right_number_of_args():

	dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')
	add_ints = dll.add_ints

	assert 7 == add_ints(3, 4)


def test_error_callargs_unconfigured_right_number_of_args_nondefault_float():

	dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')
	add_floats = dll.add_floats

	with pytest.raises(ctypes.ArgumentError):
		a = add_floats(1.2, 3.6)


def test_error_callargs_configured_too_few_args():

	dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')
	subtract_ints = dll.subtract_ints
	subtract_ints.argtypes = (ctypes.c_int16, ctypes.c_int16)
	subtract_ints.restype = ctypes.c_int16

	with pytest.raises(TypeError):
		a = subtract_ints(7)


def test_error_callargs_configured_too_many_args():

	dll = ctypes.windll.LoadLibrary('tests/demo_dll.dll')
	pow_ints = dll.pow_ints
	pow_ints.argtypes = (ctypes.c_int16, ctypes.c_int16)
	pow_ints.restype = ctypes.c_int16

	with pytest.raises(TypeError):
		a = pow_ints(7, 2, 99)
