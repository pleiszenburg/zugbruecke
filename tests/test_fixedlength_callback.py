# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_fixedlength_callback.py: Tests fixed length arrays of function pointers

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
typedef double {{ SUFFIX }} (*mathop)(double a, double b);

{{ PREFIX }} double {{ SUFFIX }} apply_op(
    mathop ops[2],
    double a,
    double b,
    int opcode
    );
"""

SOURCE = """
{{ PREFIX }} double {{ SUFFIX }} apply_op(
    mathop ops[2],
    double a,
    double b,
    int opcode
    )
{
    if (opcode >= 0 && opcode <= 1) {
        return ops[opcode](a, b);
    }
    return 0.0;
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
def test_fixedlength_callback(arch, conv, ctypes, dll_handle):
    """
    Tests fixed length arrays of callback functions
    """

    if conv == "cdll":
        FuncType = ctypes.CFUNCTYPE
    elif conv == "windll":
        FuncType = ctypes.WINFUNCTYPE
    else:
        raise ValueError("unknown calling convention", conv)

    MathOp = FuncType(ctypes.c_double, ctypes.c_double, ctypes.c_double)

    apply_op_dll = dll_handle.apply_op
    apply_op_dll.argtypes = (
        MathOp * 2,
        ctypes.c_double,
        ctypes.c_double,
        ctypes.c_int,
    )
    apply_op_dll.restype = ctypes.c_double

    @MathOp
    def add_op(a, b):
        """
        Callback function, called by DLL function
        """

        return a + b

    @MathOp
    def sub_op(a, b):
        """
        Callback function, called by DLL function
        """

        return a - b

    def apply_op(a: float, b: float, opcode: int) -> float:
        """
        User-facing wrapper around DLL function
        """

        ops = (MathOp * 2)()
        ops[0] = add_op
        ops[1] = sub_op

        return apply_op_dll(ops, a, b, opcode)

    assert pytest.approx(10.0) == apply_op(7.0, 3.0, 0)
    assert pytest.approx(4.0) == apply_op(7.0, 3.0, 1)
    assert pytest.approx(0.0) == apply_op(7.0, 3.0, 2)
