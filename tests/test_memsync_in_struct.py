# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_memsync_in_struct.py: Test bidirectional memory sync for pointers in struct

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
typedef struct bubblesort_data {
    float *a;
    int n;
} bubblesort_data;

{{ PREFIX }} void {{ SUFFIX }} bubblesort_struct(
    bubblesort_data *data
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} bubblesort_struct(
    bubblesort_data *data
    )
{
    int i, j;
    for (i = 0; i < data->n - 1; ++i)
    {
        for (j = 0; j < data->n - i - 1; ++j)
        {
            if (data->a[j] > data->a[j + 1])
            {
                float tmp = data->a[j];
                data->a[j] = data->a[j + 1];
                data->a[j + 1] = tmp;
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
def test_memsync_in_struct(arch, conv, ctypes, dll_handle):
    """
    Memsync pointer and length argument within struct that is passed as a pointer itself
    """

    class BubblesortData(ctypes.Structure):
        _fields_ = [("a", ctypes.POINTER(ctypes.c_float)), ("n", ctypes.c_int)]

    bubblesort_struct_dll = dll_handle.bubblesort_struct
    bubblesort_struct_dll.memsync = [  # Regular ctypes on Windows should ignore this statement
        dict(
            pointer = [0, "a"],  # "path" to argument containing the pointer
            length = [0, "n"],  # "path" to argument containing the length
            type = ctypes.c_float,  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
        )
    ]
    bubblesort_struct_dll.argtypes = (ctypes.POINTER(BubblesortData),)

    def bubblesort_struct(values: List[float]):
        """
        User-facing wrapper around DLL function
        """

        ct_values = ((ctypes.c_float) * len(values))(*values)
        ct_ptr = ctypes.cast(ctypes.pointer(ct_values), ctypes.POINTER(ctypes.c_float))
        bubblesort_struct_dll(ctypes.pointer(BubblesortData(ct_ptr, len(values))))
        values[:] = ct_values[:]

    data = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    bubblesort_struct(data)

    data = [round(number, 2) for number in data]
    expected = [2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34]
    diff = sum(abs(a - b) for a, b in zip(data, expected))

    assert pytest.approx(0.0, 0.0000001) == diff
