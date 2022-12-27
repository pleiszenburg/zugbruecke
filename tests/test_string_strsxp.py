# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_string_strsxp.py: R-style strings

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
{{ PREFIX }} void {{ SUFFIX }} replace_char(
    char **in_string,
    char old_letter,
    char new_letter
    );
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} replace_char(
    char **in_string,
    char old_letter,
    char new_letter
    )
{
    int i;
    for (i = 0; i < strlen((*in_string)); i++) {
        if((*in_string)[i] == old_letter) {
            (*in_string)[i] = new_letter;
        }
    }
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context, PLATFORM

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.xfail(PLATFORM == "unix", strict=True, reason="not yet implemented")
@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_r_strsxp(arch, conv, ctypes, dll_handle):
    """
    Passing R-style strings, a pointer to an array of pointers to string fragments
    """

    replace_char_dll = dll_handle.replace_char
    replace_char_dll.argtypes = (
        ctypes.POINTER(
            ctypes.POINTER(ctypes.c_char)
        ),  # Generate pointer to char manually
        ctypes.c_char,
        ctypes.c_char,
    )
    replace_char_dll.memsync = [
        dict(
            pointer = [0, -1],
            null = True,
        ),
        dict(
            pointer = [0, -1],
            null = True,
        ),
    ]

    def replace_char(string: str, old_char: str, new_char: str):
        """
        User-facing wrapper around DLL function
        """

        assert len(old_char) == 1 and len(new_char) == 1

        buffer = (ctypes.c_char_p * 1)(string.encode("utf-8"))
        ptr = ctypes.cast(
            buffer, ctypes.POINTER(ctypes.POINTER(ctypes.c_char))
        )

        replace_char_dll(
            ptr, old_char.encode("utf-8"), new_char.encode("utf-8")
        )

        return buffer[:][0].decode("utf-8")

    assert "Hellu wurld!" == replace_char("Hello world!", "o", "u")
