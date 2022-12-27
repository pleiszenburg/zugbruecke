# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_float_types.py: Tests by value argument passing and return value (float)

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
{% for DTYPE, _, _ in DTYPES %}
    {{ PREFIX }} int {{ SUFFIX }} in_mandel_{{ DTYPE }}(
        {{ DTYPE }} x0,
        {{ DTYPE }} y0,
        int n
        );
{% endfor %}
"""

SOURCE = """
{% for DTYPE, _, _ in DTYPES %}
    {{ PREFIX }} int {{ SUFFIX }} in_mandel_{{ DTYPE }}(
        {{ DTYPE }} x0,
        {{ DTYPE }} y0,
        int n
        )
    {
        /* Test if (x0,y0) is in the Mandelbrot set or not */
        {{ DTYPE }} x = 0, y = 0, xtemp;
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
{% endfor %}
"""

EXTRA = {
    "DTYPES": [
        ("float", "FLT_MIN", "FLT_MAX"),
        ("double", "DBL_MIN", "DBL_MAX"),
    ]
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
@pytest.mark.parametrize("dtype", ['float', 'double'])
def test_float_types(dtype, arch, conv, ctypes, dll_handle):
    """
    Testing float arguments for multiple float types
    """

    c_type = getattr(ctypes, f'c_{dtype:s}')

    in_mandel_dll = getattr(dll_handle, f'in_mandel_{dtype:s}')
    in_mandel_dll.argtypes = (c_type, c_type, ctypes.c_int)
    in_mandel_dll.restype = ctypes.c_int

    assert 1 == in_mandel_dll(0.0, 0.0, 500)
    assert 0 == in_mandel_dll(2.0, 1.0, 500)
