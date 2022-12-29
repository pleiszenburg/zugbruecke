# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_memsync_computed_length.py: Memory sync with lambda function

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
{{ PREFIX }} void {{ SUFFIX }} bubblesort(
    float *a,
    int u,
    int v
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} bubblesort(
    float *a,
    int u,
    int v
    )
{
    int i, j;
    int n = u * v;
    for (i = 0; i < n - 1; ++i)
    {
        for (j = 0; j < n - i - 1; ++j)
        {
            if (a[j] > a[j + 1])
            {
                float tmp = a[j];
                a[j] = a[j + 1];
                a[j + 1] = tmp;
            }
        }
    }
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import List

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_memsync_computed_length(arch, conv, ctypes, dll_handle):
    """
    Memory sync with length computed from multiple arguments via lambda function
    """

    bubblesort_dll = dll_handle.bubblesort
    bubblesort_dll.memsync = [  # Regular ctypes on Windows should ignore this statement
        dict(
            pointer = [0],  # "path" to argument containing the pointer
            length = ([1], [2]),  # "path" to arguments containing information on length
            func = "lambda x, y: x * y",  # function computing length from relevant arguments
            type = ctypes.c_float,  # type of argument
        )
    ]
    bubblesort_dll.argtypes = (
        ctypes.POINTER(ctypes.c_float),
        ctypes.c_int,
        ctypes.c_int,
    )

    def bubblesort(values: List[float], u: int, v: int):
        """
        User-facing wrapper around DLL function
        """

        ct_values = ((ctypes.c_float) * len(values))(*values)
        ct_ptr = ctypes.cast(ctypes.pointer(ct_values), ctypes.POINTER(ctypes.c_float))
        bubblesort_dll(ct_ptr, u, v)
        values[:] = ct_values[:]

    data = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    u = 2
    bubblesort(data, u = u, v = len(data) // u)

    data = [round(number, 2) for number in data]
    expected = [2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34]
    diff = sum(abs(a - b) for a, b in zip(data, expected))
    assert pytest.approx(0.0, 0.0000001) == diff
