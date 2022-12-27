# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_square_int_array_with_struct.py: Test allocation of memory by DLL in struct

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

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes

        class int_array_data(self._c.Structure):
            _fields_ = [
                ("data", self._c.POINTER(self._c.c_int16)),
                ("len", self._c.c_int16),
            ]

        self._int_array_data = int_array_data

        self._square_int_array_with_struct = dll_handle.square_int_array_with_struct
        self._square_int_array_with_struct.argtypes = (
            self._c.POINTER(self._int_array_data),
            self._c.POINTER(self._int_array_data),
        )
        self._square_int_array_with_struct.memsync = [
            {"p": [0, "data"], "l": [0, "len"], "t": "c_int16"},
            {"p": [1, "data"], "l": [1, "len"], "t": "c_int16"},
        ]

    def square_int_array_with_struct(self, in_array):

        in_array_obj = self._int_array_data()
        out_array_obj = self._int_array_data()

        in_array_obj.data = self._c.cast(
            self._c.pointer((self._c.c_int16 * len(in_array))(*in_array)),
            self._c.POINTER(self._c.c_int16),
        )
        in_array_obj.len = len(in_array)

        self._square_int_array_with_struct(in_array_obj, out_array_obj)

        return self._c.cast(
            out_array_obj.data, self._c.POINTER(self._c.c_int16 * len(in_array))
        ).contents[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_square_int_array_with_struct(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert [4, 16, 9, 25] == sample.square_int_array_with_struct([2, 4, 3, 5])
