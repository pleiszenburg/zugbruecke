# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_string_nullterminated.py: Demonstrates null terminated strings

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
{% for NAME in COPIES %}

    {{ PREFIX }} void {{ SUFFIX }} replace_char_{{ NAME }}(
        char *in_string,
        char old_letter,
        char new_letter
        );

    {{ PREFIX }} void {{ SUFFIX }} replace_wchar_{{ NAME }}(
        wchar_t *in_string,
        wchar_t old_letter,
        wchar_t new_letter
        );

{% endfor %}
"""

SOURCE = """
{% for NAME in COPIES %}

    {{ PREFIX }} void {{ SUFFIX }} replace_char_{{ NAME }}(
        char *in_string,
        char old_letter,
        char new_letter
        )
    {
        int i;
        for (i = 0; i < strlen(in_string); i++) {
            if(in_string[i] == old_letter) {
                in_string[i] = new_letter;
            }
        }
    }

    {{ PREFIX }} void {{ SUFFIX }} replace_wchar_{{ NAME }}(
        wchar_t *in_string,
        wchar_t old_letter,
        wchar_t new_letter
        )
    {
        int i;
        for (i = 0; i < wcslen(in_string); i++) {
            if(in_string[i] == old_letter) {
                in_string[i] = new_letter;
            }
        }
    }

{% endfor %}
"""

EXTRA = {
    "COPIES": ["a", "b", "c", "d"]
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPERS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def init_char(ctypes, dll_handle, suffix: str, charp: bool = False):

    ptr_type = ctypes.c_char_p if charp else ctypes.POINTER(ctypes.c_char)

    replace_char_dll = getattr(
        dll_handle,
        f'replace_char_{suffix}',
    )
    replace_char_dll.argtypes = (
        ptr_type,
        ctypes.c_char,
        ctypes.c_char,
    )
    replace_char_dll.memsync = [
        dict(
            pointer = [0],
            null = True,
        ),
    ]

    def replace_char_longer(string: str, old_char: str, new_char: str):
        """
        Create buffer of fixed (longer) length, copy string into it
        """

        assert len(old_char) == 1 and len(new_char) == 1

        BUFFER_LENGTH = 128

        buffer = ctypes.create_string_buffer(BUFFER_LENGTH)
        buffer.value = string.encode("utf-8")

        replace_char_dll(
            buffer, old_char.encode("utf-8"), new_char.encode("utf-8")
        )

        return buffer.value.decode("utf-8")

    def replace_char_equal(string: str, old_char: str, new_char: str):
        """
        Directly create buffer from string, both have equal length
        """

        assert len(old_char) == 1 and len(new_char) == 1

        buffer = ctypes.create_string_buffer(string.encode("utf-8"))

        replace_char_dll(
            buffer, old_char.encode("utf-8"), new_char.encode("utf-8")
        )

        return buffer.value.decode("utf-8")

    return (
        replace_char_longer,
        replace_char_equal,
    )


def init_wchar(ctypes, dll_handle, suffix: str, wcharp: bool = False):

    ptr_type = ctypes.c_wchar_p if wcharp else ctypes.POINTER(ctypes.c_wchar)

    replace_wchar_dll = getattr(
        dll_handle,
        f'replace_wchar_{suffix}',
    )
    replace_wchar_dll.argtypes = (
        ptr_type,
        ctypes.c_wchar,
        ctypes.c_wchar,
    )
    replace_wchar_dll.memsync = [
        dict(
            pointer = [0],
            null = True,
            unic = True,
        ),
    ]

    def replace_wchar_longer(string: str, old_char: str, new_char: str):
        """
        Create buffer of fixed (longer) length, copy string into it
        """

        assert len(old_char) == 1 and len(new_char) == 1

        BUFFER_LENGTH = 128

        buffer = ctypes.create_unicode_buffer(BUFFER_LENGTH)
        buffer.value = string

        replace_wchar_dll(buffer, old_char, new_char)

        return buffer.value

    def replace_char_equal(string: str, old_char: str, new_char: str):
        """
        Directly create buffer from string, both have equal length
        """

        assert len(old_char) == 1 and len(new_char) == 1

        buffer = ctypes.create_unicode_buffer(string)

        replace_wchar_dll(buffer, old_char, new_char)

        return buffer.value

    return (
        replace_wchar_longer,
        replace_char_equal,
    )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_char_in_longer_buffer(arch, conv, ctypes, dll_handle):
    """
    Null-terminated buffer longer than string, ctypes.POINTER(ctypes.c_char)
    """

    func, _ = init_char(ctypes, dll_handle, suffix='a', charp=False)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_char_in_equal_buffer(
    arch, conv, ctypes, dll_handle
):
    """
    Null-terminated buffer of length equal to string, ctypes.POINTER(ctypes.c_char)
    """

    _, func = init_char(ctypes, dll_handle, suffix='b', charp=False)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_char_in_longer_buffer_charp(arch, conv, ctypes, dll_handle):
    """
    Null-terminated buffer longer than string, ctypes.c_char_p
    """

    func, _ = init_char(ctypes, dll_handle, suffix='c', charp=True)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_char_in_equal_buffer_charp(
    arch, conv, ctypes, dll_handle
):
    """
    Null-terminated buffer of length equal to string, ctypes.c_char_p
    """

    _, func = init_char(ctypes, dll_handle, suffix='d', charp=True)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_wchar_in_longer_buffer(
    arch, conv, ctypes, dll_handle
):
    """
    Null-terminated buffer longer than string, ctypes.POINTER(ctypes.c_wchar)
    """

    func, _ = init_wchar(ctypes, dll_handle, suffix='a', wcharp=False)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_wchar_in_equal_buffer(
    arch, conv, ctypes, dll_handle
):
    """
    Null-terminated buffer of length equal to string, ctypes.POINTER(ctypes.c_wchar)
    """

    _, func = init_wchar(ctypes, dll_handle, suffix='b', wcharp=False)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_wchar_in_longer_buffer_charp(
    arch, conv, ctypes, dll_handle
):
    """
    Null-terminated buffer longer than string, ctypes.c_wchar_p
    """

    func, _ = init_wchar(ctypes, dll_handle, suffix='c', wcharp=True)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_wchar_in_equal_buffer_charp(
    arch, conv, ctypes, dll_handle
):
    """
    Null-terminated buffer of length equal to string, ctypes.c_wchar_p
    """

    _, func = init_wchar(ctypes, dll_handle, suffix='d', wcharp=True)

    assert "Hellu wurld!" == func("Hello world!", "o", "u")
