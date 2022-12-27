# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_string_computed_length.py: Computed length strings and memory allocation by DLL

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

    {{ PREFIX }} void {{ SUFFIX }} tag_string_{{ NAME }}(
        char *in_string,
        void *out_string
        );

{% endfor %}
"""

SOURCE = """
{% for NAME in COPIES %}

    {{ PREFIX }} void {{ SUFFIX }} tag_string_{{ NAME }}(
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

{% endfor %}
"""

EXTRA = {
    "COPIES": ["a", "b"]
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def init_tag_string(ctypes, dll_handle, suffix: str, null: bool):

    tag_string_dll = getattr(dll_handle, f'tag_string_{suffix:s}')
    tag_string_dll.argtypes = (ctypes.POINTER(ctypes.c_char), ctypes.c_void_p)

    if null:
        tag_string_dll.memsync = [
            dict(
                pointer = [0],
                null = True,
            ),
            dict(
                pointer = [1, -1],
                null = True,
            ),
        ]
    else:
        tag_string_dll.memsync = [
            dict(
                pointer = [0],
                length = ([0],),
                func = "lambda x: ctypes.sizeof(x)",
            ),
            dict(
                pointer = [1, -1],
                length = ([0],),
                func = "lambda x: ctypes.sizeof(x) + 2",
            ),
        ]

    def tag_string(string: str) -> str:
        """
        User-facing wrapper around DLL function
        """

        in_buffer = ctypes.create_string_buffer(string.encode("utf-8"))
        out_buffer = ctypes.pointer(ctypes.c_void_p())

        tag_string_dll(in_buffer, out_buffer)

        return (
            ctypes.cast(
                out_buffer.contents,
                ctypes.POINTER(ctypes.c_char * (len(in_buffer) + 2)),
            )
            .contents[:]
            .decode("utf-8")
            .rstrip("\0")
        )

    return tag_string


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_classic_null_terminated(arch, conv, ctypes, dll_handle):
    """
    Pass strings as null-terminated buffers
    """

    func = init_tag_string(ctypes, dll_handle, suffix='a', null=True)

    assert "<html>" == func("html")


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_server_side_length_computation(arch, conv, ctypes, dll_handle):
    """
    Let memsync compute the length of the string, client- and server-side
    """

    func = init_tag_string(ctypes, dll_handle, suffix='b', null=False)

    assert "<body>" == func("body")
