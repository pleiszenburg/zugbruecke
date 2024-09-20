# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_enum.py: Test enum type argument passing

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
typedef enum MODE{
    ADD = 1,
    SUB,
    MUL
} MODE;

{{ PREFIX }} double {{ SUFFIX }} operation(
    double a,
    double b,
    MODE mode
    );
"""

SOURCE = """
{{ PREFIX }} double {{ SUFFIX }} operation(
    double a,
    double b,
    MODE mode
    )
{
    if (mode == ADD) {
        return a + b;
    } else if (mode == SUB) {
        return a - b;
    } else if (mode == MUL) {
        return a * b;
    } else {
        return 0;
    }
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from enum import IntEnum, auto

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_enumtype(arch, conv, ctypes, dll_handle):
    """
    Test basic handling of enum types
    """

    class CtypesIntEnum(IntEnum):
        @classmethod
        def from_param(cls, obj):
            return int(obj)

    class MODE(CtypesIntEnum):
        ADD = auto()
        SUB = auto()
        MUL = auto()
        DIV = auto()

    operation_dll = dll_handle.operation
    operation_dll.argtypes = (ctypes.c_double, ctypes.c_double, MODE)
    operation_dll.restype = ctypes.c_double
    operation_dll.memsync = [  # Regular ctypes on Windows should ignore this statement
        dict(
            value = [0],  # "path" to argument containing the value
            length = [],  # "path" to argument containing the length
            type = ctypes.c_int,  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
            custom = MODE,  # custom datatype
            func = "lambda: 1",  # compute length
        )
    ]

    assert pytest.approx(10.0, 0.0000001) == operation_dll(7.0, 3.0, MODE.ADD)
    assert pytest.approx(4.0, 0.0000001) == operation_dll(7.0, 3.0, MODE.SUB)
    assert pytest.approx(21.0, 0.0000001) == operation_dll(7.0, 3.0, MODE.MUL)
    assert pytest.approx(0.0, 0.0000001) == operation_dll(7.0, 3.0, MODE.DIV)
