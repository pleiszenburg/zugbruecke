# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_string_byval_in_struct_pointer.py: Testing by value strings in structs by reference

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
typedef struct threewords {
    char a[5];
    char b[5];
    char c[11];
} threewords;

{{ PREFIX }} void {{ SUFFIX }} concatenate_byval_fixedlength_in_struct(
    threewords *somewords
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} concatenate_byval_fixedlength_in_struct(
    threewords *somewords
    )
{
    for (int i = 0; i < 11; i++) {
        somewords->c[i] = ' ';
    }
    for (int i = 0; i < 5; i++) {
        if (somewords->a[i] != '\\0') {
            somewords->c[i] = somewords->a[i];
        }
    }
    for (int i = 0; i < 5; i++) {
        if (somewords->b[i] != '\\0') {
            somewords->c[i + 6] = somewords->b[i];
        }
    }
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
def test_fixedlength_string_in_struct(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value within struct
    """

    class ThreeWords(ctypes.Structure):
        _fields_ = [
            ('a', ctypes.c_char * 5),
            ('b', ctypes.c_char * 5),
            ('c', ctypes.c_char * 11),
        ]

    concatenate_byval_fixedlength_in_struct_dll = dll_handle.concatenate_byval_fixedlength_in_struct
    concatenate_byval_fixedlength_in_struct_dll.argtypes = (
        ctypes.POINTER(ThreeWords),
    )

    def concatenate_byval_fixedlength_in_struct(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        somewords = ctypes.pointer(ThreeWords(a.encode('utf-8'), b.encode('utf-8'), b''))

        concatenate_byval_fixedlength_in_struct_dll(somewords)

        return somewords.contents.c.decode('utf-8')

    assert 'Hello world' == concatenate_byval_fixedlength_in_struct('Hello', 'world')
    assert 'Hell  worl ' == concatenate_byval_fixedlength_in_struct('Hell', 'worl')
