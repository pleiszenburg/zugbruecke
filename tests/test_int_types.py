# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_int_types.py: Tests by reference argument passing (int pointer) and limits (overflows)

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
    {% if ARCH == 'win64' or (ARCH == 'win32' and DTYPE != 'int64_t') %}
        {{ PREFIX }} {{ DTYPE }} {{ SUFFIX }} test_divide_{{ DTYPE }}(
            {{ DTYPE }} a,
            {{ DTYPE }} b,
            {{ DTYPE }} *remainder
            );
    {% endif %}
{% endfor %}
"""

SOURCE = """
{% for DTYPE, IMIN, IMAX in DTYPES %}
    {% if ARCH == 'win64' or (ARCH == 'win32' and DTYPE != 'int64_t') %}
        {{ PREFIX }} {{ DTYPE }} {{ SUFFIX }} test_divide_{{ DTYPE }}(
            {{ DTYPE }} a,
            {{ DTYPE }} b,
            {{ DTYPE }} *remainder
            )
        {
            if (b == 0)
            {
                *remainder = 0;
                return 0;
            }
            if (a == {{ IMIN }} && b == -1) {
                *remainder = 0;
                return {{ IMAX }};
            }
            {{ DTYPE }} quot = a / b;
            *remainder = a % b;
            return quot;
        }
    {% endif %}
{% endfor %}
"""

EXTRA = {
    "DTYPES": [
        ("int", "INT_MIN", "INT_MAX"),
        ("int8_t", "INT_LEAST8_MIN", "INT_LEAST8_MAX"),
        ("int16_t", "INT_LEAST16_MIN", "INT_LEAST16_MAX"),
        ("int32_t", "INT_LEAST32_MIN", "INT_LEAST32_MAX"),
        ("int64_t", "INT_LEAST64_MIN", "INT_LEAST64_MAX"),
    ]
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from hypothesis import (
    given,
    settings,
    strategies as st,
)
import pytest

from .lib.ctypes import get_context
from .lib.param import (
    get_int_limits,
    force_int_overflow,
    MAX_EXAMPLES,
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
@pytest.mark.parametrize("bits", [8, 16, 32, 64])
@given(data=st.data())
@settings(max_examples=MAX_EXAMPLES)
def test_int_types(data, bits, arch, conv, ctypes, dll_handle):
    """
    Tests by reference argument passing (int pointer) and limits (overflows)
    """

    if arch == 'win32' and bits == 64:
        return  # no int64_t on win32

    int_limits = get_int_limits(bits, sign=True)
    x = data.draw(st.integers(**int_limits))
    y = data.draw(st.integers(**int_limits))

    dtype = getattr(ctypes, f"c_int{bits:d}")
    divide_int = getattr(dll_handle, f"test_divide_int{bits:d}_t")
    divide_int.argtypes = (dtype, dtype, ctypes.POINTER(dtype))
    divide_int.restype = dtype

    rem_ = dtype()
    quot = divide_int(x, y, rem_)
    rem = rem_.value

    if x == int_limits['min_value'] and y == -1:

        assert (int_limits['max_value'], 0) == (quot, rem)

    elif y != 0:

        v_quot = force_int_overflow(x // y, bits, True)
        v_rem = force_int_overflow(
            abs(x) % abs(y) * (1, -1)[x < 0], bits, True
        )  # HACK C99
        if v_rem != 0 and ((x < 0) ^ (y < 0)):  # HACK C99
            v_quot = force_int_overflow(v_quot + 1, bits, True)

        assert (v_quot, v_rem) == (quot, rem)

    else:

        assert (0, 0) == (quot, rem)
