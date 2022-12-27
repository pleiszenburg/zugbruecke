# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_pointers_and_struct_malloc_by_dll.py: Test allocation of memory by DLL, returned as struct

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
typedef struct int_array_data {
    int16_t *data;
    int16_t len;
} int_array_data;

{{ PREFIX }} int_array_data {{ SUFFIX }} *fibonacci_sequence(
    int16_t len
    );
"""

SOURCE = """
{{ PREFIX }} int_array_data {{ SUFFIX }} *fibonacci_sequence(
    int16_t len
    )
{
    int16_t i;
    int_array_data *out_data = malloc(sizeof(int_array_data));
    out_data->len = len;
    out_data->data = malloc(sizeof(int16_t) * out_data->len);
    for(i = 0; i < len; i++){
        if(i == 0 || i == 1) { out_data->data[i] = 1; continue; }
        out_data->data[i] = out_data->data[i - 1] + out_data->data[i - 2];
    }
    return out_data;
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
def test_pointers_and_struct_malloc_by_dll(arch, conv, ctypes, dll_handle):
    """
    Retrieve data from memory (within returned struct) that has been allocated by DLL
    """

    class ArrayData(ctypes.Structure):
        _fields_ = [
            ("data", ctypes.POINTER(ctypes.c_int16)),
            ("len", ctypes.c_int16),
        ]

    fibonacci_sequence_dll = dll_handle.fibonacci_sequence
    fibonacci_sequence_dll.argtypes = (ctypes.c_int16,)
    fibonacci_sequence_dll.restype = ctypes.POINTER(ArrayData)
    fibonacci_sequence_dll.memsync = [
        dict(
            pointer = ["r", "data"],
            length = ["r", "len"],
            type = ctypes.c_int16,
        )
    ]

    def fibonacci_sequence(length: int) -> List[int]:
        """
        User-facing wrapper around DLL function
        """

        ptr = fibonacci_sequence_dll(length)

        return ctypes.cast(
            ptr.contents.data, ctypes.POINTER(ctypes.c_int16 * length)
        ).contents[:]

    assert [1, 1, 2, 3, 5, 8, 13, 21, 34, 55] == fibonacci_sequence(10)
