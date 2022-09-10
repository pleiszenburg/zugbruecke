# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_sqrt_int.py: Test function with single parameter

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
{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_r(
	char **in_string,
	char old_letter,
	char new_letter
	);
"""

SOURCE = """
{{ PREFIX }} void {{ SUFFIX }} replace_letter_in_null_terminated_string_r(
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
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class sample_class:
    def __init__(self, ctypes, dll_handle):

        self._c = ctypes
        self._replace_r = dll_handle.replace_letter_in_null_terminated_string_r
        self._replace_r.argtypes = (
            self._c.POINTER(
                self._c.POINTER(self._c.c_char)
            ),  # Generate pointer to char manually
            self._c.c_char,
            self._c.c_char,
        )
        self._replace_r.memsync = [
            ({"p": [0, -1], "n": True}, {"p": [0, -1], "n": True})
        ]

    def replace_r(self, in_string, old_letter, new_letter):

        string_buffer = (self._c.c_char_p * 1)(in_string.encode("utf-8"))
        string_buffer_p = self._c.cast(
            string_buffer, self._c.POINTER(self._c.POINTER(self._c.c_char))
        )

        self._replace_r(
            string_buffer_p, old_letter.encode("utf-8"), new_letter.encode("utf-8")
        )

        return string_buffer[:][0].decode("utf-8")


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.xfail(PLATFORM == "unix", strict=True, reason="not yet implemented")
@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_r_strsxp(arch, conv, ctypes, dll_handle):

    sample = sample_class(ctypes, dll_handle)
    assert "zetegehube" == sample.replace_r("zategahuba", "a", "e")
