# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_divide.py: Tests by reference argument passing (int pointer)

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
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context
from .lib.param import MAX_EXAMPLES

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
    x=st.integers(min_value=-1 * 2 ** 31, max_value=2 ** 31 - 1),
    y=st.integers(min_value=-1 * 2 ** 31, max_value=2 ** 31 - 1),
)
@settings(max_examples=MAX_EXAMPLES)
def test_divide(x, y, arch, conv, ctypes, dll_handle):

    divide_int = dll_handle.divide_int
    divide_int.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
    divide_int.restype = ctypes.c_int

    rem_ = ctypes.c_int()
    quot = divide_int(x, y, rem_)
    rem = rem_.value

    if x == -1 * 2 ** 31 and y == -1:

        assert (2 ** 31 - 1, 0) == (quot, rem)

    elif y != 0:

        v_quot = x // y
        v_rem = abs(x) % abs(y) * (1, -1)[x < 0]  # HACK C99
        if v_rem != 0 and ((x < 0) ^ (y < 0)):  # HACK C99
            v_quot += 1

        assert (v_quot, v_rem) == (quot, rem)

    else:

        assert (0, 0) == (quot, rem)
