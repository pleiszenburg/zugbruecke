# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_gauss_elimination.py: Tests 2D fixed length arrays w/ floats

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
{{ PREFIX }} void {{ SUFFIX }} gauss_elimination(
	float (*A)[3][4],
	float (*x)[3]
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} gauss_elimination(
	float (*A)[3][4],
	float (*x)[3]
	)
{

	int i, j, k, n = 3;
	float c, sum = 0.0;

	for(j = 0; j < n; j++)
	{
		for(i = j + 1; i < n; i++)
		{
			c = (*A)[i][j] / (*A)[j][j];
			for(k = 0; k <= n; k++)
			{
				(*A)[i][k] = (*A)[i][k] - c * (*A)[j][k];
			}
		}
	}

	(*x)[n - 1] = (*A)[n - 1][n] / (*A)[n - 1][n - 1];

	for(i = n - 2; i >= 0; i--)
	{
		sum = 0;
		for(j = i + 1; j < n; j++)
		{
			sum = sum + (*A)[i][j] * (*x)[j];
		}
		(*x)[i] = ((*A)[i][n] - sum) / (*A)[i][i];
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
        self._gauss_elimination = dll_handle.gauss_elimination
        self._gauss_elimination.argtypes = (
            self._c.POINTER(self._c.c_float * 4 * 3),
            self._c.POINTER(self._c.c_float * 3),
        )

    def gauss_elimination(self, A):

        N = 3
        if len(A) != N or len(A[0]) != N + 1:
            raise  # TODO

        x = [0 for eq in range(N)]
        _A = (self._c.c_float * (N + 1) * N)(*(tuple(eq) for eq in A))
        _x = (self._c.c_float * N)(*tuple(x))
        self._gauss_elimination(self._c.pointer(_A), self._c.pointer(_x))
        for index, eq in enumerate(A):
            eq[:] = _A[index][:]
        x[:] = _x[:]

        return x


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_gauss_elimination(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    eq_sys = [[1, 2, 3, 2], [1, 1, 1, 2], [3, 3, 1, 0]]
    eq_sys_solution = sample.gauss_elimination(eq_sys)

    assert (
        [5.0, -6.0, 3.0],
        [[1.0, 2.0, 3.0, 2.0], [0.0, -1.0, -2.0, 0.0], [0.0, 0.0, -2.0, -6.0]],
    ) == (eq_sys_solution, eq_sys)
