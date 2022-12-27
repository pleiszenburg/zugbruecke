# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_no_arguments.py: Test function call without parameters

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
{{ PREFIX }} int16_t {{ SUFFIX }} get_const_int_a(void);

{{ PREFIX }} int16_t {{ SUFFIX }} get_const_int_b(void);

{{ PREFIX }} int16_t {{ SUFFIX }} get_const_int_c(void);
"""

SOURCE = """
{{ PREFIX }} int16_t {{ SUFFIX }} get_const_int_a(void)
{
    return (int16_t)sqrt(49);
}

{{ PREFIX }} int16_t {{ SUFFIX }} get_const_int_b(void)
{
    return (int16_t)sqrt(36);
}

{{ PREFIX }} int16_t {{ SUFFIX }} get_const_int_c(void)
{
    return (int16_t)sqrt(25);
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_no_configuration(arch, conv, ctypes, dll_handle):
    """
    Argtypes is not configured
    """

    get_const_int = dll_handle.get_const_int_a
    get_const_int.restype = ctypes.c_int16

    assert 7 == get_const_int()


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_empty_tuple(arch, conv, ctypes, dll_handle):
    """
    Argtypes is set to empty tuple
    """

    get_const_int = dll_handle.get_const_int_b
    get_const_int.argtypes = tuple()
    get_const_int.restype = ctypes.c_int16

    assert 6 == get_const_int()


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_empty_list(arch, conv, ctypes, dll_handle):
    """
    Argtypes is set to empty list
    """

    get_const_int = dll_handle.get_const_int_c
    get_const_int.argtypes = []
    get_const_int.restype = ctypes.c_int16

    assert 5 == get_const_int()
