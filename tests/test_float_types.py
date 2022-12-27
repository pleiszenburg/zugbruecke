# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_in_mantel.py: Tests by value argument passing and return value (float)

    Required to run on platform / side: [UNIX, WINE]

    Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
{{ PREFIX }} int {{ SUFFIX }} in_mandel(
	double x0,
	double y0,
	int n
	);
"""

SOURCE = """
/* Test if (x0,y0) is in the Mandelbrot set or not */
{{ PREFIX }} int {{ SUFFIX }} in_mandel(
	double x0,
	double y0,
	int n
	)
{
	double x = 0, y = 0, xtemp;
	while (n > 0)
	{
		xtemp = x * x - y * y + x0;
		y = 2 * x * y + y0;
		x = xtemp;
		n -= 1;
		if (x * x + y * y > 4) return 0;
	}
	return 1;
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):

        self.in_mandel = dll_handle.in_mandel
        self.in_mandel.argtypes = (ctypes.c_double, ctypes.c_double, ctypes.c_int)
        self.in_mandel.restype = (
            ctypes.c_int
        )  # TODO: sizeof(int) win32 vs win64 vs unix


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_in_mantel_inside(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert 1 == sample.in_mandel(0.0, 0.0, 500)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_in_mantel_outside(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert 0 == sample.in_mandel(2.0, 1.0, 500)
