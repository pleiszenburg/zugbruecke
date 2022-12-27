# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_pointers_and_array_in_struct_malloc_by_dll.py: Test array pointer in struct and allocation of memory by DLL

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

{{ PREFIX }} void {{ SUFFIX }} square_int_array_with_struct(
    int_array_data *in_array,
    int_array_data *out_array
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} square_int_array_with_struct(
    int_array_data *in_array,
    int_array_data *out_array
    )
{
    int i;
    out_array->len = in_array->len;
    out_array->data = malloc(sizeof(int16_t) * out_array->len);
    for(i = 0; i < in_array->len; i++)
    {
        out_array->data[i] = in_array->data[i] * in_array->data[i];
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
def test_pointers_and_array_in_struct_malloc_by_dll(arch, conv, ctypes, dll_handle):
    """
    Test array pointer in struct and allocation of memory by DLL
    """

    class ArrayData(ctypes.Structure):
        _fields_ = [
            ("data", ctypes.POINTER(ctypes.c_int16)),
            ("len", ctypes.c_int16),
        ]

    square_int_array_with_struct_dll = dll_handle.square_int_array_with_struct
    square_int_array_with_struct_dll.argtypes = (
        ctypes.POINTER(ArrayData),
        ctypes.POINTER(ArrayData),
    )
    square_int_array_with_struct_dll.memsync = [
        dict(
            pointer = [0, "data"],
            length = [0, "len"],
            type = ctypes.c_int16,
        ),
        dict(
            pointer = [1, "data"],
            length = [1, "len"],
            type = ctypes.c_int16,
        ),
    ]

    def square_int_array_with_struct(data: List[int]) -> List[int]:
        """
        User-facing wrapper around DLL function
        """

        in_struct = ArrayData(
            ctypes.cast(
                ctypes.pointer((ctypes.c_int16 * len(data))(*data)),
                ctypes.POINTER(ctypes.c_int16),
            ),
            len(data),
        )
        out_struct = ArrayData()

        square_int_array_with_struct_dll(in_struct, out_struct)

        return ctypes.cast(
            out_struct.data, ctypes.POINTER(ctypes.c_int16 * len(data))
        ).contents[:]

    assert [4, 16, 9, 25] == square_int_array_with_struct([2, 4, 3, 5])
