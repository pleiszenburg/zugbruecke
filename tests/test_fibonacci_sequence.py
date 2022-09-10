# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_fibonacci_sequence.py: Test allocation of memory by DLL, returned as struct

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

{{ PREFIX }} int_array_data {{ SUFFIX }} *fibonacci_sequence(
	int16_t len
	);
"""

SOURCE = """
{{ PREFIX }} int_array_data {{ SUFFIX }} *fibonacci_sequence(
	int16_t len
	)
{
	int16_t i;
	int_array_data *out_data = malloc(sizeof(int_array_data));
	out_data->len = len;
	out_data->data = malloc(sizeof(int16_t) * out_data->len);
	for(i = 0; i < len; i++){
		if(i == 0 || i == 1) { out_data->data[i] = 1; continue; }
		out_data->data[i] = out_data->data[i - 1] + out_data->data[i - 2];
	}
	return out_data;
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

        self._fibonacci_sequence = dll_handle.fibonacci_sequence
        self._fibonacci_sequence.argtypes = (self._c.c_int16,)
        self._fibonacci_sequence.restype = self._c.POINTER(int_array_data)
        self._fibonacci_sequence.memsync = [
            {"p": ["r", "data"], "l": ["r", "len"], "t": "c_int16"}
        ]

    def fibonacci_sequence(self, length):

        out_array_obj = self._fibonacci_sequence(length)

        return self._c.cast(
            out_array_obj.contents.data, self._c.POINTER(self._c.c_int16 * length)
        ).contents[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fibonacci_sequence(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert [1, 1, 2, 3, 5, 8, 13, 21, 34, 55] == sample.fibonacci_sequence(10)
