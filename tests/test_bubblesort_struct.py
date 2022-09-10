# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_bubblesort_struct.py: Test bidirectional memory sync for pointers in struct

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
typedef struct bubblesort_data {
	float *a;
	int n;
} bubblesort_data;

{{ PREFIX }} void {{ SUFFIX }} bubblesort_struct(
	bubblesort_data *data
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} bubblesort_struct(
	bubblesort_data *data
	)
{
	int i, j;
	for (i = 0; i < data->n - 1; ++i)
	{
		for (j = 0; j < data->n - i - 1; ++j)
		{
			if (data->a[j] > data->a[j + 1])
			{
				float tmp = data->a[j];
				data->a[j] = data->a[j + 1];
				data->a[j + 1] = tmp;
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

        class bubblesort_data(self._c.Structure):
            _fields_ = [("a", self._c.POINTER(self._c.c_float)), ("n", self._c.c_int)]

        self.bubblesort_data = bubblesort_data

        self._bubblesort_struct = dll_handle.bubblesort_struct
        self._bubblesort_struct.memsync = [  # Regular ctypes on Windows should ignore this statement
            {
                "p": [0, "a"],  # "path" to argument containing the pointer
                "l": [0, "n"],  # "path" to argument containing the length
                "t": "c_float",  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
            }
        ]
        self._bubblesort_struct.argtypes = (self._c.POINTER(self.bubblesort_data),)

    def bubblesort_struct(self, values):

        ctypes_float_values = ((self._c.c_float) * len(values))(*values)
        ctypes_float_pointer_firstelement = self._c.cast(
            self._c.pointer(ctypes_float_values), self._c.POINTER(self._c.c_float)
        )

        data = self.bubblesort_data(ctypes_float_pointer_firstelement, len(values))

        self._bubblesort_struct(data)
        values[:] = ctypes_float_values[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_bubblesort_struct(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    test_vector = [5.74, 3.72, 6.28, 8.6, 9.34, 6.47, 2.05, 9.09, 4.39, 4.75]
    sample.bubblesort_struct(test_vector)
    test_vector = [round(element, 2) for element in test_vector]
    result_vector = [2.05, 3.72, 4.39, 4.75, 5.74, 6.28, 6.47, 8.6, 9.09, 9.34]
    vector_diff = sum(
        [
            abs(test_vector[index] - result_vector[index])
            for index in range(len(result_vector))
        ]
    )

    assert pytest.approx(0.0, 0.0000001) == vector_diff
