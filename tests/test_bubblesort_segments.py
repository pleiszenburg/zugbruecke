# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_bubblesort_segments.py: Memory sync with lambda function

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
{{ PREFIX }} void {{ SUFFIX }} bubblesort_segments(
	float *a,
	int number_of_segments,
	int elements_per_segment
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} bubblesort_segments(
	float *a,
	int number_of_segments,
	int elements_per_segment
	)
{
	int i, j;
	int n = number_of_segments * elements_per_segment;
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

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._bubblesort_segments = dll_handle.bubblesort_segments
        self._bubblesort_segments.memsync = [  # Regular ctypes on Windows should ignore this statement
            {
                "p": [0],  # "path" to argument containing the pointer
                "l": ([1], [2]),  # "path" to arguments containing information on length
                "f": "lambda x, y: x * y",  # function computing length from relevant arguments
                "t": "c_float",  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
            }
        ]
        self._bubblesort_segments.argtypes = (
            self._c.POINTER(self._c.c_float),
            self._c.c_int,
            self._c.c_int,
        )

    def bubblesort_segments(self, values, number_of_segments, elements_per_segment):

        ctypes_float_values = ((self._c.c_float) * len(values))(*values)
        ctypes_float_pointer_firstelement = self._c.cast(
            self._c.pointer(ctypes_float_values), self._c.POINTER(self._c.c_float)
        )
        self._bubblesort_segments(
            ctypes_float_pointer_firstelement, number_of_segments, elements_per_segment
        )
        values[:] = ctypes_float_values[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_bubblesort(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]  # 5, 2
    segments = 2
    sample.bubblesort_segments(test_vector, segments, len(test_vector) // 2)
    test_vector = [round(element, 2) for element in test_vector]
    result_vector = [2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34]
    vector_diff = sum(
        [
            abs(test_vector[index] - result_vector[index])
            for index in range(len(result_vector))
        ]
    )

    assert pytest.approx(0.0, 0.0000001) == vector_diff
