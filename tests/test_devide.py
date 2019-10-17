# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_devide.py: Tests by reference argument passing (int pointer)

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
# C
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

HEADER = """
int __stdcall DEMODLL divide_int(
	int a,
	int b,
	int *remainder
	);
"""

SOURCE = """
int __stdcall DEMODLL divide_int(
	int a,
	int b,
	int *remainder
	)
{
	int quot = a / b;
	*remainder = a % b;
	return quot;
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_dll_handles

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize('ctypes,dll_handle', get_dll_handles(__file__))
def test_devide(ctypes, dll_handle):

	x, y = 11, 3 # TODO generate x and y with hypothesis

	divide_int = dll_handle.divide_int
	divide_int.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
	divide_int.restype = ctypes.c_int

	rem_ = ctypes.c_int()
	quot = divide_int(x, y, rem_)
	rem = rem_.value

	assert (x // y, x % y) == (quot, rem)
