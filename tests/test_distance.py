# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_distance.py: Tests by value struct type passing and return value

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
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):
        class Point(ctypes.Structure):
            _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

        self.Point = Point

        self.distance = dll_handle.distance
        self.distance.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
        self.distance.restype = ctypes.c_double

        self._distance_pointer = dll_handle.distance_pointer
        self._distance_pointer.argtypes = (ctypes.POINTER(Point), ctypes.POINTER(Point))
        self._distance_pointer.restype = ctypes.POINTER(ctypes.c_double)

    def distance_pointer(self, in1, in2):

        return self._distance_pointer(in1, in2).contents.value


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_distance(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    p1 = sample.Point(1, 2)
    p2 = sample.Point(4, 5)

    assert pytest.approx(4.242640687119285, 0.0000001) == sample.distance(p1, p2)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_distance_pointer(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    p1 = sample.Point(1, 2)
    p2 = sample.Point(4, 5)

    assert pytest.approx(4.242640687119285, 0.0000001) == sample.distance_pointer(
        p1, p2
    )
