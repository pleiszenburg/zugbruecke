# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_pointers_byref.py: Testing "light-weight pointers"

    Required to run on platform / side: [UNIX, WINE]

    Copyright (C) 2017-2023 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
typedef struct subparam {
    int a;
    int b;
    int diff;
} subparam;

typedef struct mulparam {
    float a;
    float b;
    float prod;
} mulparam;

{{ PREFIX }} void {{ SUFFIX }} add_int(
    int a,
    int b,
    int *sum
    );

{{ PREFIX }} void {{ SUFFIX }} sub_int(
    subparam *values
    );

{{ PREFIX }} void {{ SUFFIX }} mul_float(
    mulparam *values
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} add_int(
    int a,
    int b,
    int *sum
    )
{
    *sum = a + b;
}

{{ PREFIX }} void {{ SUFFIX }} sub_int(
    subparam *values
    )
{
    values->diff = values->a - values->b;
}

{{ PREFIX }} void {{ SUFFIX }} mul_float(
    mulparam *values
    )
{
    values->prod = values->a * values->b;
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_pointers_byref_simple(arch, conv, ctypes, dll_handle):
    """
    Tests byref with simple data type
    """

    add_int = dll_handle.add_int
    add_int.argtypes = (ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int))

    sum_ = ctypes.c_int()
    add_int(3, 4, ctypes.byref(sum_))
    assert sum_.value == 7


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_pointers_byref_struct_int(arch, conv, ctypes, dll_handle):
    """
    Tests byref with struct data type containing int
    """

    class SubParam(ctypes.Structure):
        _fields_ = [
            ("a", ctypes.c_int),
            ("b", ctypes.c_int),
            ("diff", ctypes.c_int),
        ]

    sub_int = dll_handle.sub_int
    sub_int.argtypes = (ctypes.POINTER(SubParam),)

    param = SubParam(17, 15, 0)
    sub_int(ctypes.byref(param))
    assert param.diff == 2


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_pointers_byref_struct_float(arch, conv, ctypes, dll_handle):
    """
    Tests byref with struct data type containing float
    """

    class MulParam(ctypes.Structure):
        _fields_ = [
            ("a", ctypes.c_float),
            ("b", ctypes.c_float),
            ("prod", ctypes.c_float),
        ]

    mul_float = dll_handle.mul_float
    mul_float.argtypes = (ctypes.POINTER(MulParam),)

    param = MulParam(5.0, 6.0, 0.0)
    mul_float(ctypes.byref(param))
    assert pytest.approx(30.0) == param.prod
