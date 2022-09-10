# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_callback_simple.py: Demonstrates callback routines as arguments

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
typedef int16_t {{ SUFFIX }} (*conveyor_belt)(int16_t index);

{{ PREFIX }} int16_t {{ SUFFIX }} sum_elements_from_callback(
	int16_t len,
	conveyor_belt get_data
	);
"""

SOURCE = """
{{ PREFIX }} int16_t {{ SUFFIX }} sum_elements_from_callback(
	int16_t len,
	conveyor_belt get_data
	)
{

	int16_t sum = 0;
	int16_t i;

	for(i = 0; i < len; i++)
	{
		sum += get_data(i);
	}

	return sum;

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
    def __init__(self, conv, ctypes, dll_handle):

        if conv == "cdll":
            func_type = ctypes.CFUNCTYPE
        elif conv == "windll":
            func_type = ctypes.WINFUNCTYPE
        else:
            raise ValueError("unknown calling convention", conv)
        conveyor_belt = func_type(ctypes.c_int16, ctypes.c_int16)

        self._sum_elements_from_callback = dll_handle.sum_elements_from_callback
        self._sum_elements_from_callback.argtypes = (ctypes.c_int16, conveyor_belt)
        self._sum_elements_from_callback.restype = ctypes.c_int16

        self.DATA = [1, 6, 8, 4, 9, 7, 4, 2, 5, 2]

        @conveyor_belt
        def get_data(index):
            print((index, self.DATA[index]))
            return self.DATA[index]

        self.__get_data__ = get_data

    def sum_elements_from_callback(self):

        return self._sum_elements_from_callback(len(self.DATA), self.__get_data__)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_callback_simple(arch, conv, ctypes, dll_handle):

    sample = sample_class(conv, ctypes, dll_handle)

    assert 48 == sample.sum_elements_from_callback()
