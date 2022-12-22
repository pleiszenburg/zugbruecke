# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_customtype.py: Test custom ctypes data type argument passing

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

from array import array
from typing import Any, List, Tuple, Union

from .lib.ctypes import get_context

import numpy as np
import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_customtype(arch, conv, ctypes, dll_handle):
    """
    Test basic handling of custom ctypes data types
    """

    class DoubleArrayType:
        """
        Custom ctypes data type
        """

        def from_param(self, param: Any) -> Any:
            """
            Called by ctypes/zugbruecke, dispatches to different implementations
            """

            typename = type(param).__name__

            if hasattr(self, "from_" + typename):
                return getattr(self, "from_" + typename)(param)
            if isinstance(param, ctypes.Array):
                return param

            raise TypeError(f"Can't convert {typename:s}")

        def from_array(self, param: array) -> ctypes.POINTER(ctypes.c_double):
            """
            Implementation for basic Python array (from standard library)
            """

            if param.typecode != "d":
                raise TypeError("must be an array of doubles")
            ptr, _ = param.buffer_info()
            return ctypes.cast(ptr, ctypes.POINTER(ctypes.c_double * len(param)))

        def from_list(self, param: Union[List[float], Tuple[float, ...]]) -> ctypes.c_double:
            """
            Implementation for Python list (and tuple)
            """

            # does not need to be a pointer IN THIS CASE (can be though)
            return ((ctypes.c_double) * len(param))(*param)

        from_tuple = from_list

        def from_ndarray(self, param: np.ndarray) -> ctypes.POINTER(ctypes.c_double):
            """
            Implementation for numpy.ndarray
            """

            return param.ctypes.data_as(ctypes.POINTER(ctypes.c_double))

    DoubleArray = DoubleArrayType()
    avg_dll = dll_handle.avg
    avg_dll.memsync = [  # Regular ctypes on Windows should ignore this statement
        dict(
            pointer = [0],  # "path" to argument containing the pointer
            length = [1],  # "path" to argument containing the length
            type = ctypes.c_double,  # type of argument (optional, default char/byte): sizeof(type) * length == bytes
            custom = DoubleArray,  # custom datatype
        )
    ]
    avg_dll.argtypes = (DoubleArray, ctypes.c_int)
    avg_dll.restype = ctypes.c_double

    for blob in (
        [1, 2, 3, 4],
        [1.0, 2.0, 3.0, 4.0],
        (1.0, 2.0, 3.0, 4.0),
        np.array([1.0, 2.0, 3.0, 4.0], dtype = 'f8'),
        array('d', [1.0, 2.0, 3.0, 4.0]),
    ):
        assert pytest.approx(2.5, 0.0000001) == avg_dll(blob, len(blob))
