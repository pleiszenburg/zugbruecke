# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_null_terminated_string.py: Demonstrates null terminated strings

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
{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_a(
	char *in_string,
	char old_letter,
	char new_letter
	);

{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_b(
	char *in_string,
	char old_letter,
	char new_letter
	);

{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_unicode_a(
	wchar_t *in_string,
	wchar_t old_letter,
	wchar_t new_letter
	);

{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_unicode_b(
	wchar_t *in_string,
	wchar_t old_letter,
	wchar_t new_letter
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_a(
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

{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_b(
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

{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_unicode_a(
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

{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_unicode_b(
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
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class_a:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._replace_letter_in_null_terminated_string = (
            dll_handle.replace_letter_in_null_terminated_string_a
        )
        self._replace_letter_in_null_terminated_string.argtypes = (
            self._c.POINTER(self._c.c_char),  # Generate pointer to char manually
            self._c.c_char,
            self._c.c_char,
        )
        self._replace_letter_in_null_terminated_string.memsync = [{"p": [0], "n": True}]

    def replace_letter_in_null_terminated_string(
        self, in_string, old_letter, new_letter
    ):

        BUFFER_LENGTH = 128

        string_buffer = self._c.create_string_buffer(BUFFER_LENGTH)
        string_buffer.value = in_string.encode("utf-8")

        self._replace_letter_in_null_terminated_string(
            string_buffer, old_letter.encode("utf-8"), new_letter.encode("utf-8")
        )

        return string_buffer.value.decode("utf-8")

    def replace_letter_in_null_terminated_string_buff(
        self, in_string, old_letter, new_letter
    ):

        string_buffer = self._c.create_string_buffer(in_string.encode("utf-8"))

        self._replace_letter_in_null_terminated_string(
            string_buffer, old_letter.encode("utf-8"), new_letter.encode("utf-8")
        )

        return string_buffer.value.decode("utf-8")


class sample_class_b:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._replace_letter_in_null_terminated_string = (
            dll_handle.replace_letter_in_null_terminated_string_b
        )
        self._replace_letter_in_null_terminated_string.argtypes = (
            self._c.c_char_p,  # Use built-in char pointer type
            self._c.c_char,
            self._c.c_char,
        )
        self._replace_letter_in_null_terminated_string.memsync = [{"p": [0], "n": True}]

    def replace_letter_in_null_terminated_string(
        self, in_string, old_letter, new_letter
    ):

        BUFFER_LENGTH = 128

        string_buffer = self._c.create_string_buffer(BUFFER_LENGTH)
        string_buffer.value = in_string.encode("utf-8")

        self._replace_letter_in_null_terminated_string(
            string_buffer, old_letter.encode("utf-8"), new_letter.encode("utf-8")
        )

        return string_buffer.value.decode("utf-8")

    def replace_letter_in_null_terminated_string_buff(
        self, in_string, old_letter, new_letter
    ):

        string_buffer = self._c.create_string_buffer(in_string.encode("utf-8"))

        self._replace_letter_in_null_terminated_string(
            string_buffer, old_letter.encode("utf-8"), new_letter.encode("utf-8")
        )

        return string_buffer.value.decode("utf-8")


class sample_class_unicode_a:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._replace_letter_in_null_terminated_string_unicode = (
            dll_handle.replace_letter_in_null_terminated_string_unicode_a
        )
        self._replace_letter_in_null_terminated_string_unicode.argtypes = (
            self._c.POINTER(self._c.c_wchar),  # Generate pointer to wchar manually
            self._c.c_wchar,
            self._c.c_wchar,
        )
        self._replace_letter_in_null_terminated_string_unicode.memsync = [
            {"p": [0], "n": True, "w": True}
        ]

    def replace_letter_in_null_terminated_string_unicode(
        self, in_string, old_letter, new_letter
    ):

        BUFFER_LENGTH = 128

        string_buffer = self._c.create_unicode_buffer(BUFFER_LENGTH)
        string_buffer.value = in_string

        self._replace_letter_in_null_terminated_string_unicode(
            string_buffer, old_letter, new_letter
        )

        return string_buffer.value

    def replace_letter_in_null_terminated_string_buff_unicode(
        self, in_string, old_letter, new_letter
    ):

        string_buffer = self._c.create_unicode_buffer(in_string)

        self._replace_letter_in_null_terminated_string_unicode(
            string_buffer, old_letter, new_letter
        )

        return string_buffer.value


class sample_class_unicode_b:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._replace_letter_in_null_terminated_string_unicode = (
            dll_handle.replace_letter_in_null_terminated_string_unicode_b
        )
        self._replace_letter_in_null_terminated_string_unicode.argtypes = (
            self._c.c_wchar_p,  # Use built-in wchar pointer type
            self._c.c_wchar,
            self._c.c_wchar,
        )
        self._replace_letter_in_null_terminated_string_unicode.memsync = [
            {"p": [0], "n": True, "w": True}
        ]

    def replace_letter_in_null_terminated_string_unicode(
        self, in_string, old_letter, new_letter
    ):

        BUFFER_LENGTH = 128

        string_buffer = self._c.create_unicode_buffer(BUFFER_LENGTH)
        string_buffer.value = in_string

        self._replace_letter_in_null_terminated_string_unicode(
            string_buffer, old_letter, new_letter
        )

        return string_buffer.value

    def replace_letter_in_null_terminated_string_buff_unicode(
        self, in_string, old_letter, new_letter
    ):

        string_buffer = self._c.create_unicode_buffer(in_string)

        self._replace_letter_in_null_terminated_string_unicode(
            string_buffer, old_letter, new_letter
        )

        return string_buffer.value


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_a(arch, conv, ctypes, dll_handle):

    sample = sample_class_a(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_buff_a(
    arch, conv, ctypes, dll_handle
):

    sample = sample_class_a(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string_buff(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_b(arch, conv, ctypes, dll_handle):

    sample = sample_class_b(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_buff_b(
    arch, conv, ctypes, dll_handle
):

    sample = sample_class_b(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string_buff(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_unicode_a(
    arch, conv, ctypes, dll_handle
):

    sample = sample_class_unicode_a(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string_unicode(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_buff_unicode_a(
    arch, conv, ctypes, dll_handle
):

    sample = sample_class_unicode_a(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string_buff_unicode(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_unicode_b(
    arch, conv, ctypes, dll_handle
):

    sample = sample_class_unicode_b(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string_unicode(
        "zategahuba", "a", "e"
    )


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_replace_letter_in_null_terminated_string_buff_unicode_b(
    arch, conv, ctypes, dll_handle
):

    sample = sample_class_unicode_b(ctypes, dll_handle)

    assert "zetegehube" == sample.replace_letter_in_null_terminated_string_buff_unicode(
        "zategahuba", "a", "e"
    )
