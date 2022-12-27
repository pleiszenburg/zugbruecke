# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_error_restype.py: Test error handling when malformed return types are passed

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
{{ PREFIX }} int16_t {{ SUFFIX }} sqrt_int(
    int16_t a
    );

{{ PREFIX }} int16_t {{ SUFFIX }} add_ints(
    int16_t a,
    int16_t b
    );

{{ PREFIX }} float {{ SUFFIX }} add_floats(
    float a,
    float b
    );

{{ PREFIX }} double {{ SUFFIX }} add_doubles(
    double a,
    double b
    );
"""

SOURCE = """
{{ PREFIX }} int16_t {{ SUFFIX }} sqrt_int(
    int16_t a
    )
{
    return sqrt(a);
}

{{ PREFIX }} int16_t {{ SUFFIX }} add_ints(
    int16_t a,
    int16_t b
    )
{
    return a + b;
}

{{ PREFIX }} float {{ SUFFIX }} add_floats(
    float a,
    float b
    )
{
    return a + b;
}

{{ PREFIX }} double {{ SUFFIX }} add_doubles(
    double a,
    double b
    )
{
    return a + b;
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
def test_error_restype_wrong_type(arch, conv, ctypes, dll_handle):
    """
    Restype is not provided as a ctypes type or anything else useful
    """

    sqrt_int = dll_handle.sqrt_int

    with pytest.raises(TypeError):
        sqrt_int.restype = []


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_error_restype_unconfigured_int(
    arch, conv, ctypes, dll_handle
):
    """
    No configuration for restype, function returns int
    """

    add_ints = dll_handle.add_ints

    assert 7 == add_ints(3, 4)


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
@pytest.mark.skip(reason="test passes on its own but makes original ctypes crash in later tests")
def test_error_restype_unconfigured_nondefault_float(
    arch, conv, ctypes, dll_handle
):
    """
    No configuration for restype, ctypes assumes int, func returns float, value is garbage
    """

    add_floats = dll_handle.add_floats
    add_floats.argtypes = (ctypes.c_float, ctypes.c_float)

    value = add_floats(1.2, 3.6)

    assert isinstance(value, int)
    assert pytest.approx(float(value)) != 4.8  # garbage


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
@pytest.mark.skip(reason="test passes on its own but makes original ctypes crash in later tests")
def test_error_restype_unconfigured_nondefault_double(
    arch, conv, ctypes, dll_handle
):
    """
    No configuration for restype, ctypes assumes int, func returns double, value is garbage
    """

    add_doubles = dll_handle.add_doubles
    add_doubles.argtypes = (ctypes.c_double, ctypes.c_double)

    value = add_doubles(ctypes.c_double(1.2), ctypes.c_double(3.6))

    assert isinstance(value, int)
    assert pytest.approx(float(value)) != 4.8  # garbage
