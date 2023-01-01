# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_fixedlength_struct.py: Tests fixed length arrays of structs

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
typedef struct manynumbers {
    float a, b, c, d, e, f;
} manynumbers;

{{ PREFIX }} void {{ SUFFIX }} sum_members(
    manynumbers numbers[10],
    manynumbers *sum
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} sum_members(
    manynumbers numbers[10],
    manynumbers *sum
    )
{
    sum->a = 0.0;
    sum->b = 0.0;
    sum->c = 0.0;
    sum->d = 0.0;
    sum->e = 0.0;
    sum->f = 0.0;
    for (int i = 0; i < 10; i++)
    {
        sum->a += numbers[i].a;
        sum->b += numbers[i].b;
        sum->c += numbers[i].c;
        sum->d += numbers[i].d;
        sum->e += numbers[i].e;
        sum->f += numbers[i].f;
    }
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
def test_fixedlength_struct(arch, conv, ctypes, dll_handle):
    """
    Tests fixed length arrays of structs
    """

    class ManyNumbers(ctypes.Structure):
        _fields_ = [
            ('a', ctypes.c_float),
            ('b', ctypes.c_float),
            ('c', ctypes.c_float),
            ('d', ctypes.c_float),
            ('e', ctypes.c_float),
            ('f', ctypes.c_float),
        ]

    sum_members_dll = dll_handle.sum_members
    sum_members_dll.argtypes = (
        ManyNumbers * 10,
        ctypes.POINTER(ManyNumbers),
    )

    numbers = (ManyNumbers * 10)()
    for idx in range(10):
        numbers[idx].a = 1 + idx * 10
        numbers[idx].b = 2 + idx * 10
        numbers[idx].c = 3 + idx * 10
        numbers[idx].d = 4 + idx * 10
        numbers[idx].e = 5 + idx * 10
        numbers[idx].f = 6 + idx * 10
    sum_ = ManyNumbers()

    sum_members_dll(numbers, ctypes.pointer(sum_))

    assert all((
        sum_.a == 460,
        sum_.b == 470,
        sum_.c == 480,
        sum_.d == 490,
        sum_.e == 500,
        sum_.f == 510,
    ))
