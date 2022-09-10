# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_square_int_array.py: Test allocation of memory by DLL

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

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._square_int_array = dll_handle.square_int_array
        self._square_int_array.argtypes = (
            self._c.POINTER(self._c.c_int16),
            self._c.c_void_p,
            self._c.c_int16,
        )
        self._square_int_array.memsync = [
            {"p": [0], "l": [2], "t": "c_int16"},
            {"p": [1, -1], "l": [2], "t": "c_int16"},
        ]

    def square_int_array(self, in_array):

        in_array_p = self._c.cast(
            self._c.pointer((self._c.c_int16 * len(in_array))(*in_array)),
            self._c.POINTER(self._c.c_int16),
        )
        out_array_p = self._c.pointer(self._c.c_void_p())

        self._square_int_array(in_array_p, out_array_p, self._c.c_int16(len(in_array)))

        return self._c.cast(
            out_array_p.contents, self._c.POINTER(self._c.c_int16 * len(in_array))
        ).contents[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_square_int_array(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert [4, 16, 9, 25] == sample.square_int_array([2, 4, 3, 5])
