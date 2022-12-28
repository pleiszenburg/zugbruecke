# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_fixedlength_string.py: Tests fixed length char buffers with & without pointers

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
{% for W, T in UNIC %}

    typedef struct {{ W }}twowords {
        {{ W }}char{{ T }} a[5];
        {{ W }}char{{ T }} b[5];
    } {{ W }}twowords;

    {% for NAME in COPIES %}

        {{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength_{{ W }}{{ NAME }}(
            {{ W }}char{{ T }} a[5],
            {{ W }}char{{ T }} b[5],
            {{ W }}char{{ T }} (*out)[11]
            );

        {{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength_in_struct_{{ W }}{{ NAME }}(
            {{ W }}twowords *somewords,
            {{ W }}char{{ T }} (*out)[11]
            );

    {% endfor %}

{% endfor %}
"""

SOURCE = """
{% for W, T in UNIC %}

    {% for NAME in COPIES %}

        {{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength_{{ W }}{{ NAME }}(
            {{ W }}char{{ T }} a[5],
            {{ W }}char{{ T }} b[5],
            {{ W }}char{{ T }} (*out)[11]
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

        {{ PREFIX }} void {{ SUFFIX }} concatenate_fixedlength_in_struct_{{ W }}{{ NAME }}(
            {{ W }}twowords *somewords,
            {{ W }}char{{ T }} (*out)[11]
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

{% endfor %}
"""

EXTRA = {
    "COPIES": ["f", "g"],
    "UNIC": [("", ""), ("w", "_t")],
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
def test_fixedlength_string(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value
    """

    concatenate_fixedlength_dll = dll_handle.concatenate_fixedlength_f
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
def test_fixedlength_string_unicode(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value, UNICODE
    """

    concatenate_fixedlength_dll = dll_handle.concatenate_fixedlength_wf
    concatenate_fixedlength_dll.argtypes = (
        ctypes.c_wchar * 5,
        ctypes.c_wchar * 5,
        ctypes.POINTER(ctypes.c_wchar * 11),
    )

    def concatenate_fixedlength(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        c_wchar_array5 = ctypes.c_wchar * 5

        a_wchars = c_wchar_array5()
        a_wchars.value = a
        b_wchars = c_wchar_array5()
        b_wchars.value = b
        out = ctypes.pointer((ctypes.c_wchar * 11)())

        concatenate_fixedlength_dll(a_wchars, b_wchars, out)

        return out.contents[:]

    assert 'Hello world' == concatenate_fixedlength('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_variation(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value; variation on buffer creation
    """

    concatenate_fixedlength_dll = dll_handle.concatenate_fixedlength_g
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

        a_bytes = a.encode('utf-8')
        a_chars = c_char_array5()  # create array buffer from type
        a_chars[:len(a_bytes)] = a_bytes
        b_bytes = b.encode('utf-8')
        b_chars = c_char_array5()  # create array buffer from type
        b_chars[:len(b_bytes)] = b_bytes
        out = ctypes.pointer((ctypes.c_char * 11)())

        concatenate_fixedlength_dll(a_chars, b_chars, out)

        return out.contents[:].decode('utf-8')

    assert 'Hello world' == concatenate_fixedlength('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_variation_unicode(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value; variation on buffer creation, UNICODE
    """

    concatenate_fixedlength_dll = dll_handle.concatenate_fixedlength_wg
    concatenate_fixedlength_dll.argtypes = (
        ctypes.c_wchar * 5,
        ctypes.c_wchar * 5,
        ctypes.POINTER(ctypes.c_wchar * 11),
    )

    def concatenate_fixedlength(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        c_wchar_array5 = ctypes.c_wchar * 5

        a_wchars = c_wchar_array5()  # create array buffer from type
        a_wchars[:len(a)] = a
        b_wchars = c_wchar_array5()  # create array buffer from type
        b_wchars[:len(b)] = b
        out = ctypes.pointer((ctypes.c_wchar * 11)())

        concatenate_fixedlength_dll(a_wchars, b_wchars, out)

        return out.contents[:]

    assert 'Hello world' == concatenate_fixedlength('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_in_struct(arch, conv, ctypes, dll_handle):
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
def test_fixedlength_string_in_struct_unicode(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value within struct, UNICODE
    """

    class TwoWords(ctypes.Structure):
        _fields_ = [
            ('a', ctypes.c_wchar * 5),
            ('b', ctypes.c_wchar * 5),
        ]

    cconcatenate_fixedlength_in_struct_dll = dll_handle.concatenate_fixedlength_in_struct_wf
    cconcatenate_fixedlength_in_struct_dll.argtypes = (
        ctypes.POINTER(TwoWords),
        ctypes.POINTER(ctypes.c_wchar * 11),
    )

    def concatenate_fixedlength_in_struct(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        somewords = ctypes.pointer(TwoWords(a, b))
        out = ctypes.pointer((ctypes.c_wchar * 11)())

        cconcatenate_fixedlength_in_struct_dll(somewords, out)

        return out.contents[:]

    assert 'Hello world' == concatenate_fixedlength_in_struct('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength_in_struct('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_in_struct_setattr(arch, conv, ctypes, dll_handle):
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

        somewords = TwoWords()
        setattr(somewords, 'a', a.encode('utf-8'))
        setattr(somewords, 'b', b.encode('utf-8'))
        out = ctypes.pointer((ctypes.c_char * 11)())

        cconcatenate_fixedlength_in_struct_dll(ctypes.pointer(somewords), out)

        return out.contents[:].decode('utf-8')

    assert 'Hello world' == concatenate_fixedlength_in_struct('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength_in_struct('Hell', 'worl')


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_fixedlength_string_in_struct_setattr_unicode(arch, conv, ctypes, dll_handle):
    """
    Test char arrays, fixed length, passed by value within struct via setattr, UNICODE
    """

    class TwoWords(ctypes.Structure):
        _fields_ = [
            ('a', ctypes.c_wchar * 5),
            ('b', ctypes.c_wchar * 5),
        ]

    cconcatenate_fixedlength_in_struct_dll = dll_handle.concatenate_fixedlength_in_struct_wg
    cconcatenate_fixedlength_in_struct_dll.argtypes = (
        ctypes.POINTER(TwoWords),
        ctypes.POINTER(ctypes.c_wchar * 11),
    )

    def concatenate_fixedlength_in_struct(a: str, b: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        assert len(a) <= 5 and len(b) <= 5

        somewords = TwoWords()
        setattr(somewords, 'a', a)
        setattr(somewords, 'b', b)
        out = ctypes.pointer((ctypes.c_wchar * 11)())

        cconcatenate_fixedlength_in_struct_dll(ctypes.pointer(somewords), out)

        return out.contents[:]

    assert 'Hello world' == concatenate_fixedlength_in_struct('Hello', 'world')
    assert 'Hell  worl ' == concatenate_fixedlength_in_struct('Hell', 'worl')
