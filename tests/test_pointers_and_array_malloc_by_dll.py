# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_pointers_and_array_malloc_by_dll.py: Test array pointer and allocation of memory by DLL

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
{{ PREFIX }} void {{ SUFFIX }} square_int_array(
    int16_t *in_array,
    void *out_array,
    int16_t len
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} square_int_array(
    int16_t *in_array,
    void *out_array,
    int16_t len
    )
{
    int i;
    int16_t **out_array_p = out_array;
    *out_array_p = malloc(sizeof(int16_t) * len);
    for(i = 0; i < len; i++)
    {
        (*out_array_p)[i] = in_array[i] * in_array[i];
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
def test_pointers_and_array_malloc_by_dll(arch, conv, ctypes, dll_handle):

    square_int_array_dll = dll_handle.square_int_array
    square_int_array_dll.argtypes = (
        ctypes.POINTER(ctypes.c_int16),
        ctypes.c_void_p,
        ctypes.c_int16,
    )
    square_int_array_dll.memsync = [
        dict(
            pointer = [0],
            length = [2],
            type = ctypes.c_int16,
        ),
        dict(
            pointer = [1, -1],
            length = [2],
            type = ctypes.c_int16,
        ),
    ]

    def square_int_array(data: List[int]) -> List[int]:
        """
        User-facing wrapper around DLL function
        """

        in_ptr = ctypes.cast(
            ctypes.pointer((ctypes.c_int16 * len(data))(*data)),
            ctypes.POINTER(ctypes.c_int16),
        )
        out_ptr = ctypes.pointer(ctypes.c_void_p())

        square_int_array_dll(in_ptr, out_ptr, ctypes.c_int16(len(data)))

        return ctypes.cast(
            out_ptr.contents, ctypes.POINTER(ctypes.c_int16 * len(data))
        ).contents[:]

    assert [4, 16, 9, 25] == square_int_array([2, 4, 3, 5])
