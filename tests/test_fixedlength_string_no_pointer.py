# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_fixedlength_string_no_pointer.py: Tests fixed length char buffers without pointers

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
typedef struct twowords {
    char a[5];
    char b[5];
} twowords;

{{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength(
    char a[5],
    char b[5],
    char (*out)[11]
    );

{% for NAME in COPIES %}
    {{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength_in_struct_{{ NAME }}(
        twowords *somewords,
        char (*out)[11]
        );
{% endfor %}
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength(
    char a[5],
    char b[5],
    char (*out)[11]
    )
{
    for (int i = 0; i < 11; i++) {
        (*out)[i] = ' ';
    }
    for (int i = 0; i < 5; i++) {
        if (a[i] != '\\0') {
            (*out)[i] = a[i];
        }
    }
    for (int i = 0; i < 5; i++) {
        if (b[i] != '\\0') {
            (*out)[i + 6] = b[i];
        }
    }
}

{% for NAME in COPIES %}
    {{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength_in_struct_{{ NAME }}(
        twowords *somewords,
        char (*out)[11]
        )
    {
        for (int i = 0; i < 11; i++) {
            (*out)[i] = ' ';
        }
        for (int i = 0; i < 5; i++) {
            if (somewords->a[i] != '\\0') {
                (*out)[i] = somewords->a[i];
            }
        }
        for (int i = 0; i < 5; i++) {
            if (somewords->b[i] != '\\0') {
                (*out)[i + 6] = somewords->b[i];
            }
        }
    }
{% endfor %}
"""

EXTRA = {
    "COPIES": ["f", "g"]
}

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
def test_fixedlength_string_no_pointer(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value
    """

    concatenate_fixedlength_dll = dll_handle.concatenate_fixedlength
    concatenate_fixedlength_dll.argtypes = (
        ctypes.c_char * 5,
        ctypes.c_char * 5,
        ctypes.POINTER(ctypes.c_char * 11),
    )

    def concatenate_fixedlength(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        c_char_array5 = ctypes.c_char * 5

        a_chars = c_char_array5()
        a_chars.value = a.encode('utf-8')
        b_chars = c_char_array5()
        b_chars.value = b.encode('utf-8')
        out = ctypes.pointer((ctypes.c_char * 11)())

        concatenate_fixedlength_dll(a_chars, b_chars, out)

        return out.contents[:].decode('utf-8')

    assert 'Hello world' == concatenate_fixedlength('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_no_pointer_in_struct(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value within struct
    """

    class TwoWords(ctypes.Structure):
        _fields_ = [
            ('a', ctypes.c_char * 5),
            ('b', ctypes.c_char * 5),
        ]

    cconcatenate_fixedlength_in_struct_dll = dll_handle.concatenate_fixedlength_in_struct_f
    cconcatenate_fixedlength_in_struct_dll.argtypes = (
        ctypes.POINTER(TwoWords),
        ctypes.POINTER(ctypes.c_char * 11),
    )

    def concatenate_fixedlength_in_struct(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        somewords = ctypes.pointer(TwoWords(a.encode('utf-8'), b.encode('utf-8')))
        out = ctypes.pointer((ctypes.c_char * 11)())

        cconcatenate_fixedlength_in_struct_dll(somewords, out)

        return out.contents[:].decode('utf-8')

    assert 'Hello world' == concatenate_fixedlength_in_struct('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength_in_struct('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_no_pointer_in_struct_setattr(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value within struct via setattr
    """

    class TwoWords(ctypes.Structure):
        _fields_ = [
            ('a', ctypes.c_char * 5),
            ('b', ctypes.c_char * 5),
        ]

    cconcatenate_fixedlength_in_struct_dll = dll_handle.concatenate_fixedlength_in_struct_g
    cconcatenate_fixedlength_in_struct_dll.argtypes = (
        ctypes.POINTER(TwoWords),
        ctypes.POINTER(ctypes.c_char * 11),
    )

    def concatenate_fixedlength_in_struct(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        c_char_array5 = ctypes.c_char * 5

        somewords = TwoWords()
        setattr(somewords, 'a', a.encode('utf-8'))
        setattr(somewords, 'b', b.encode('utf-8'))
        out = ctypes.pointer((ctypes.c_char * 11)())

        cconcatenate_fixedlength_in_struct_dll(ctypes.pointer(somewords), out)

        return out.contents[:].decode('utf-8')

    assert 'Hello world' == concatenate_fixedlength_in_struct('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength_in_struct('Hell', 'worl')
