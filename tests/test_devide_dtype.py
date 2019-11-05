# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_devide_dtype.py: Tests by reference argument passing (int pointer)

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
{% for DTYPE in DTYPES %}
	{{ PREFIX }} {{ DTYPE }} {{ SUFFIX }} test_divide_{{ DTYPE }}(
		{{ DTYPE }} a,
		{{ DTYPE }} b,
		{{ DTYPE }} *remainder
		);
{% endfor %}
"""

SOURCE = """
{% for DTYPE in DTYPES %}
	{{ PREFIX }} {{ DTYPE }} {{ SUFFIX }} test_divide_{{ DTYPE }}(
		{{ DTYPE }} a,
		{{ DTYPE }} b,
		{{ DTYPE }} *remainder
		)
	{
		if (b == 0)
		{
			*remainder = 0;
			return 0;
		}
		{{ DTYPE }} quot = a / b;
		*remainder = a % b;
		return quot;
	}
{% endfor %}
"""

EXTRA = {
	'DTYPES': ['int', 'int8_t', 'int16_t', 'int32_t'] # TODO: 'int64_t' only on win64
	}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_dll_handles

from hypothesis import given, strategies as st
import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def _int_limits(bits, sign = True):
	assert isinstance(bits, int)
	assert bits in (8, 16, 32, 64)
	assert isinstance(sign, bool)
	if sign:
		return {'min_value': -1 * 2 ** (bits - 1), 'max_value': 2 ** (bits - 1) - 1}
	else:
		return {'min_value': 0, 'max_value': 2 ** bits - 1}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.parametrize('ctypes,dll_handle', get_dll_handles(__file__))
@pytest.mark.parametrize('bits', [8, 16, 32])
@given(data = st.data())
def test_devide_dtype(data, bits, ctypes, dll_handle):

	x = data.draw(st.integers(**_int_limits(bits, sign = True)))
	y = data.draw(st.integers(**_int_limits(bits, sign = True)))

	dtype = getattr(ctypes, 'c_int{BITS:d}'.format(BITS = bits))
	divide_int = getattr(dll_handle, 'test_divide_int{BITS:d}_t'.format(BITS = bits))
	divide_int.argtypes = (dtype, dtype, ctypes.POINTER(dtype))
	divide_int.restype = dtype

	rem_ = dtype()
	quot = divide_int(x, y, rem_)
	rem = rem_.value

	if y != 0:

		v_quot = x // y
		v_rem = abs(x) % abs(y) * (1, -1)[x < 0] # HACK C99
		if v_rem != 0 and ((x < 0) ^ (y < 0)): # HACK C99
			v_quot += 1

		assert (v_quot, v_rem) == (quot, rem)

	else:

		assert (0, 0) == (quot, rem)
