# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_int_minimal.py: Tests by basic integer handling, with/without pointers

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
{{ PREFIX }} int {{ SUFFIX }} divide_int(
    int a,
    int b,
    int *remainder
    );

{{ PREFIX }} int {{ SUFFIX }} gcd(
    int x,
    int y
    );

{{ PREFIX }} int16_t {{ SUFFIX }} sqrt_int(
    int16_t a
    );
"""

SOURCE = """
{{ PREFIX }} int {{ SUFFIX }} divide_int(
    int a,
    int b,
    int *remainder
    )
{
    if (b == 0)
    {
        *remainder = 0;
        return 0;
    }
    if (a == INT_MIN && b == -1) {
        return INT_MAX;
    }
    int quot = a / b;
    *remainder = a % b;
    return quot;
}

{{ PREFIX }} int {{ SUFFIX }} gcd(
    int x,
    int y
    )
{
    /* Compute the greatest common divisor */
    int g = y;
    while (x > 0)
    {
        g = x;
        x = y % x;
        y = g;
    }
    return g;
}

{{ PREFIX }} int16_t {{ SUFFIX }} sqrt_int(
    int16_t a
    )
{
    return (int16_t)sqrt(a);
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context
from .lib.param import MAX_EXAMPLES, get_int_limits

from hypothesis import (
    given,
    settings,
    strategies as st,
)
import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
@given(
    x=st.integers(**get_int_limits(32, sign=True)),
    y=st.integers(**get_int_limits(32, sign=True)),
)
@settings(max_examples=MAX_EXAMPLES)
def test_int_with_pointer(x, y, arch, conv, ctypes, dll_handle):
    """
    Tests by reference argument passing (int pointer) for c_int
    """

    divide_int = dll_handle.divide_int
    divide_int.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
    divide_int.restype = ctypes.c_int

    rem_ = ctypes.c_int()
    quot = divide_int(x, y, rem_)
    rem = rem_.value

    int_limits = get_int_limits(32, sign=True)

    if x == int_limits['min_value'] and y == -1:

        assert (int_limits['max_value'], 0) == (quot, rem)

    elif y != 0:

        v_quot = x // y
        v_rem = abs(x) % abs(y) * (1, -1)[x < 0]  # HACK C99
        if v_rem != 0 and ((x < 0) ^ (y < 0)):  # HACK C99
            v_quot += 1

        assert (v_quot, v_rem) == (quot, rem)

    else:

        assert (0, 0) == (quot, rem)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_int_without_pointer(arch, conv, ctypes, dll_handle):
    """
    Test simple int passing
    """

    gcd = dll_handle.gcd
    gcd.argtypes = (
        ctypes.c_int,
        ctypes.c_int,
    )
    gcd.restype = ctypes.c_int

    assert 7 == gcd(35, 42)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_int_with_size_without_pointer(arch, conv, ctypes, dll_handle):
    """
    Test simple int passing with size
    """

    sqrt_int = dll_handle.sqrt_int
    sqrt_int.argtypes = (ctypes.c_int16,)
    sqrt_int.restype = ctypes.c_int16

    assert 3 == sqrt_int(9)
