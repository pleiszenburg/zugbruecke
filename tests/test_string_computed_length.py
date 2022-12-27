# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_tag_string.py: Demonstrates memory allocation by DLL

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
{{ PREFIX }} void {{ SUFFIX }} tag_string_a(
	char *in_string,
	void *out_string
	);

{{ PREFIX }} void {{ SUFFIX }} tag_string_b(
	char *in_string,
	void *out_string
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} tag_string_a(
	char *in_string,
	void *out_string
	)
{
	int str_len = strlen(in_string);

	char **out_string_p = out_string;
	*out_string_p = malloc(sizeof(char) * (str_len + 2));
	strncpy((*out_string_p) + 1, in_string, str_len);
	(*out_string_p)[0] = '<';
	(*out_string_p)[str_len + 1] = '>';
	(*out_string_p)[str_len + 2] = '\0';
}

{{ PREFIX }} void {{ SUFFIX }} tag_string_b(
	char *in_string,
	void *out_string
	)
{
	int str_len = strlen(in_string);

	char **out_string_p = out_string;
	*out_string_p = malloc(sizeof(char) * (str_len + 2));
	strncpy((*out_string_p) + 1, in_string, str_len);
	(*out_string_p)[0] = '<';
	(*out_string_p)[str_len + 1] = '>';
	(*out_string_p)[str_len + 2] = '\0';
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
        self._tag_string = dll_handle.tag_string_a
        self._tag_string.argtypes = (self._c.POINTER(self._c.c_char), self._c.c_void_p)
        self._tag_string.memsync = [
            {"p": [0], "l": ([0],), "f": "lambda x: ctypes.sizeof(x)"},
            {"p": [1, -1], "l": ([0],), "f": "lambda x: ctypes.sizeof(x) + 2"},
        ]

    def tag_string(self, in_string):

        in_buffer = self._c.create_string_buffer(in_string.encode("utf-8"))
        out_buffer = self._c.pointer(self._c.c_void_p())

        self._tag_string(in_buffer, out_buffer)

        return (
            self._c.cast(
                out_buffer.contents,
                self._c.POINTER(self._c.c_char * (len(in_buffer) + 2)),
            )
            .contents[:]
            .decode("utf-8")
            .rstrip("\0")
        )


class sample_class_b:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._tag_string = dll_handle.tag_string_b
        self._tag_string.argtypes = (self._c.POINTER(self._c.c_char), self._c.c_void_p)
        self._tag_string.memsync = [{"p": [0], "n": True}, {"p": [1, -1], "n": True}]

    def tag_string(self, in_string):

        in_buffer = self._c.create_string_buffer(in_string.encode("utf-8"))
        out_buffer = self._c.pointer(self._c.c_void_p())

        self._tag_string(in_buffer, out_buffer)

        return (
            self._c.cast(
                out_buffer.contents,
                self._c.POINTER(self._c.c_char * (len(in_buffer) + 2)),
            )
            .contents[:]
            .decode("utf-8")
            .rstrip("\0")
        )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_tag_string(arch, conv, ctypes, dll_handle):

    sample = sample_class_a(ctypes, dll_handle)

    assert "<html>" == sample.tag_string("html")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_tag_string_serverside_length_computation(arch, conv, ctypes, dll_handle):

    sample = sample_class_b(ctypes, dll_handle)

    assert "<body>" == sample.tag_string("body")
