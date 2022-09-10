# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_mix_rgb_colors.py: Tests 1D fixed length arrays with ints

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
{{ PREFIX }} void {{ SUFFIX }} mix_rgb_colors(
	int8_t color_a[3],
	int8_t color_b[3],
	int8_t *color_mixed
	);
"""

SOURCE = """
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

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._mix_rgb_colors = dll_handle.mix_rgb_colors
        self._mix_rgb_colors.argtypes = (
            self._c.c_ubyte * 3,
            self._c.c_ubyte * 3,
            self._c.POINTER(self._c.c_ubyte * 3),
        )

    def mix_rgb_colors(self, color_a, color_b):

        color_type = self._c.c_ubyte * 3
        ctypes_color_a = color_type(*tuple(color_a))
        ctypes_color_b = color_type(*tuple(color_b))
        mixed_color = color_type()
        self._mix_rgb_colors(
            ctypes_color_a, ctypes_color_b, self._c.pointer(mixed_color)
        )
        return mixed_color[:]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_mix_rgb_colors(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)

    assert [45, 35, 30] == sample.mix_rgb_colors([10, 20, 40], [80, 50, 20])
