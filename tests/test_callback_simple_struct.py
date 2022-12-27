# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_callback_simple_struct.py: Demonstrates callback in struct

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
typedef int16_t {{ SUFFIX }} (*conveyor_belt)(int16_t index);

typedef struct conveyor_belt_data {
    int16_t len;
    conveyor_belt get_data;
} conveyor_belt_data;

{{ PREFIX }} int16_t {{ SUFFIX }} sum_elements_from_callback_in_struct(
    struct conveyor_belt_data *data
    );
"""

SOURCE = """
{{ PREFIX }} int16_t {{ SUFFIX }} sum_elements_from_callback_in_struct(
    struct conveyor_belt_data *data
    )
{

    int16_t sum = 0;
    int16_t i;

    for(i = 0; i < data->len; i++)
    {
        sum += data->get_data(i);
    }

    return sum;

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
def test_callback_simple(arch, conv, ctypes, dll_handle):
    """
    Demonstrates callback in struct
    """

    if conv == "cdll":
        func_type = ctypes.CFUNCTYPE
    elif conv == "windll":
        func_type = ctypes.WINFUNCTYPE
    else:
        raise ValueError("unknown calling convention", conv)

    ConveyorBeltFunc = func_type(ctypes.c_int16, ctypes.c_int16)

    class ConveyorBeltData(ctypes.Structure):
        _fields_ = [("len", ctypes.c_int16), ("get_data", ConveyorBeltFunc)]

    sum_elements_from_callback_in_struct_dll = (
        dll_handle.sum_elements_from_callback_in_struct
    )
    sum_elements_from_callback_in_struct_dll.argtypes = (
        ctypes.POINTER(ConveyorBeltData),
    )
    sum_elements_from_callback_in_struct_dll.restype = ctypes.c_int16

    DATA = [1, 6, 8, 4, 9, 7, 4, 2, 5, 2]

    @ConveyorBeltFunc
    def get_data(index):
        """
        Callback function, called by DLL function
        """

        print(index, DATA[index])
        return DATA[index]

    def sum_elements_from_callback_in_struct(data: List[int]) -> int:
        """
        User-facing wrapper around DLL function
        """

        return sum_elements_from_callback_in_struct_dll(ConveyorBeltData(len(data), get_data))

    assert 48 == sum_elements_from_callback_in_struct(DATA)
