# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_fixedlength_arrays.py: Tests fixed length arrays with & without pointers

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

{{ PREFIX }} void {{ SUFFIX }} mix_rgb_colors(
    int8_t color_a[3],
    int8_t color_b[3],
    int8_t *color_mixed
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

{{ PREFIX }} void {{ SUFFIX }} mix_rgb_colors(
    int8_t color_a[3],
    int8_t color_b[3],
    int8_t *color_mixed
    )
{
    int i;
    for (i = 0; i < 3; i++)
    {
        color_mixed[i] = (color_a[i] + color_b[i]) / 2;
    }
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import List

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_pointers_to_fixedlength_nd_arrays(arch, conv, ctypes, dll_handle):
    """
    Test pointers to arrays of fixed length, n-dimensional
    """

    gauss_elimination_dll = dll_handle.gauss_elimination
    gauss_elimination_dll.argtypes = (
        ctypes.POINTER(ctypes.c_float * 4 * 3),
        ctypes.POINTER(ctypes.c_float * 3),
    )

    def gauss_elimination(A: List[List[float]]) -> List[float]:
        """
        User-facing wrapper around DLL function
        """

        N = 3
        if len(A) != N or len(A[0]) != N + 1:
            raise ValueError

        x = [0 for eq in range(N)]
        _A = (ctypes.c_float * (N + 1) * N)(*(tuple(eq) for eq in A))
        _x = (ctypes.c_float * N)(*tuple(x))

        gauss_elimination_dll(ctypes.pointer(_A), ctypes.pointer(_x))

        for index, eq in enumerate(A):
            eq[:] = _A[index][:]
        x[:] = _x[:]

        return x

    eq_sys = [[1.0, 2.0, 3.0, 2.0], [1.0, 1.0, 1.0, 2.0], [3.0, 3.0, 1.0, 0.0]]
    solution = gauss_elimination(eq_sys)

    assert (
        [5.0, -6.0, 3.0],
        [[1.0, 2.0, 3.0, 2.0], [0.0, -1.0, -2.0, 0.0], [0.0, 0.0, -2.0, -6.0]],
    ) == (solution, eq_sys)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_1d_arrays_by_value(arch, conv, ctypes, dll_handle):
    """
    Testing fixed-length 1D arrays by value (and as a pointer)
    """

    mix_rgb_colors_dll = dll_handle.mix_rgb_colors
    mix_rgb_colors_dll.argtypes = (
        ctypes.c_ubyte * 3,
        ctypes.c_ubyte * 3,
        ctypes.POINTER(ctypes.c_ubyte * 3),
    )

    def mix_rgb_colors(a: List[int], b: List[int]) -> List[int]:
        """
        User-facing wrapper around DLL function
        """

        color_type = ctypes.c_ubyte * 3
        ct_a = color_type(*tuple(a))
        ct_b = color_type(*tuple(b))
        ct_m = color_type()
        mix_rgb_colors_dll(
            ct_a, ct_b, ctypes.pointer(ct_m)
        )
        return ct_m[:]

    assert [45, 35, 30] == mix_rgb_colors([10, 20, 40], [80, 50, 20])
