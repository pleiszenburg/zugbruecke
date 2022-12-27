# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_pointers_and_struct.py: Tests by value struct type passing and return value

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
typedef struct point {
    double x, y;
} point;

{{ PREFIX }} double {{ SUFFIX }} distance(
    point *p1,
    point *p2
    );

{{ PREFIX }} double {{ SUFFIX }} *distance_pointer(
    point *p1,
    point *p2
    );
"""

SOURCE = """
{{ PREFIX }} double {{ SUFFIX }} distance(
    point *p1,
    point *p2
    )
{
    return hypot(p1->x - p2->x, p1->y - p2->y);
}

{{ PREFIX }} double {{ SUFFIX }} *distance_pointer(
    point *p1,
    point *p2
    )
{
    double *distance_p = (double *)malloc(sizeof(double));
    *distance_p = hypot(p1->x - p2->x, p1->y - p2->y);
    return distance_p;
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
def test_pointer_args(arch, conv, ctypes, dll_handle):
    """
    Pointer arguments, pass structs directly though, get result by value
    """

    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    distance_dll = dll_handle.distance
    distance_dll.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
    distance_dll.restype = ctypes.c_double

    assert pytest.approx(4.242640687119285, 0.0000001) == distance_dll(
        Point(1, 2), Point(4, 5)
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_pointer_args_and_retval(arch, conv, ctypes, dll_handle):
    """
    Pointer arguments, pass structs directly though, get result as pointer (allocated by DLL)
    """

    class Point(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    distance_pointer_dll = dll_handle.distance_pointer
    distance_pointer_dll.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
    distance_pointer_dll.restype = ctypes.POINTER(ctypes.c_double)

    assert pytest.approx(4.242640687119285, 0.0000001) == distance_pointer_dll(
        Point(1, 2), Point(4, 5)
    ).contents.value
