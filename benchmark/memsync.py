# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    benchmark/memsync.py: Minimal call, two parameters, no pointers or memsync

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
{{ PREFIX }} void {{ SUFFIX }} bubblesort(
    float *a,
    int n
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} bubblesort(
    float *a,
    int n
    )
{
    int i, j;
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

from math import isclose
from typing import List

from tests.lib.benchmark import benchmark

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# BENCHMARK(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def init(ctypes, dll_handle, conv):

    bubblesort_dll = dll_handle.bubblesort
    bubblesort_dll.argtypes = (ctypes.POINTER(ctypes.c_float), ctypes.c_int)
    bubblesort_dll.memsync = [  # Regular ctypes on Windows should ignore this statement
        dict(
            pointer = [0],  # "path" to argument containing the pointer
            length = [1],  # "path" to argument containing the length
            type = ctypes.c_float,  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
        )
    ]

    def bubblesort(values: List[float]):
        """
        User-facing wrapper around DLL function
        """

        ct_values = ((ctypes.c_float) * len(values))(*values)
        ct_ptr = ctypes.cast(ctypes.pointer(ct_values), ctypes.POINTER(ctypes.c_float))
        bubblesort_dll(ct_ptr, len(values))
        values[:] = ct_values[:]

    return bubblesort


@benchmark(fn = __file__, initializer = init)
def memsync(ctypes, func):
    """
    The "memsync" benchmark is a basic test of bidirectional memory synchronization
    via a ``memsync`` directive for a pointer argument,
    an array of single-precision floating point numbers.
    The benchmark uses 10 numbers per array.
    It is passed to the DLL function,
    next to the array's length as an ``c_int``.
    The DLL function performs a classic bubblesort algorithm in-place
    on the passed / synchronized memory.
    """

    data = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    expected = [2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34]

    func(data)

    diff = sum(abs(round(a, 2) - b) for a, b in zip(data, expected))
    assert isclose(0.0, diff)
