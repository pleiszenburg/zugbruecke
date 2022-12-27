# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_error_memsync.py: Checks for proper error handling of memsync definitions

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
{{ PREFIX }} int16_t {{ SUFFIX }} sub_ints(
    int16_t a,
    int16_t b
    );
"""

SOURCE = """
{{ PREFIX }} int16_t {{ SUFFIX }} sub_ints(
    int16_t a,
    int16_t b
    )
{
    return a - b;
}
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .lib.ctypes import get_context

import pytest

from sys import platform

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_memsync_on_routine_not_list(arch, conv, ctypes, dll_handle):
    """
    Memsync on DLL function has wrong type
    """

    sub_ints = dll_handle.sub_ints

    if any(platform.startswith(os_name) for os_name in ["linux", "darwin", "freebsd"]):
        with pytest.raises(TypeError):
            sub_ints.memsync = {}
    elif platform.startswith("win"):
        sub_ints.memsync = {}


@pytest.mark.parametrize("arch,conv,ctypes,dll_handle", get_context(__file__))
def test_memsync_on_callback_not_list(arch, conv, ctypes, dll_handle):
    """
    Memsync on callback function type has wrong type
    """

    if conv == "cdll":
        func_type = ctypes.CFUNCTYPE
    elif conv == "windll":
        func_type = ctypes.WINFUNCTYPE
    else:
        raise ValueError("unknown calling convention", conv)

    conveyor_belt = func_type(ctypes.c_int16, ctypes.c_int16)

    if any(platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']):
        with pytest.raises(TypeError):
            conveyor_belt.memsync = {}
    elif platform.startswith('win'):
        conveyor_belt.memsync = {}
