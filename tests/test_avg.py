# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_avg.py: Test custom datatype argument passing as pointer

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
{{ PREFIX }} double {{ SUFFIX }} avg(
	double *a,
	int n
	);
"""

SOURCE = """
{{ PREFIX }} double {{ SUFFIX }} avg(
	double *a,
	int n
	)
{
	int i;
	double total = 0.0;
	for (i = 0; i < n; i++)
	{
		total += a[i];
	}
	return total / n;
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
        class DoubleArrayType:
            def from_param(self, param):
                typename = type(param).__name__
                if hasattr(self, "from_" + typename):
                    return getattr(self, "from_" + typename)(param)
                elif isinstance(param, ctypes.Array):
                    return param
                else:
                    raise TypeError("Can't convert %s" % typename)

            def from_array(self, param):
                if param.typecode != "d":
                    raise TypeError("must be an array of doubles")
                ptr, _ = param.buffer_info()
                return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double))

            def from_list(self, param):
                val = ((ctypes.c_double) * len(param))(*param)
                return val

            from_tuple = from_list

            def from_ndarray(self, param):
                return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

        DoubleArray = DoubleArrayType()
        self._avg = dll_handle.avg
        self._avg.memsync = [  # Regular ctypes on Windows should ignore this statement
            {
                "p": [0],  # "path" to argument containing the pointer
                "l": [1],  # "path" to argument containing the length
                "t": "c_double",  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
                "_c": DoubleArray,  # custom datatype
            }
        ]
        self._avg.argtypes = (DoubleArray, ctypes.c_int)
        self._avg.restype = ctypes.c_double

    def avg(self, values):

        return self._avg(values, len(values))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_avg(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert pytest.approx(2.5, 0.0000001) == sample.avg([1, 2, 3, 4])
