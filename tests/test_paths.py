# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_paths.py: Converting paths between Unix and Wine/Windows formats

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
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import pytest

from .lib.ctypes import get_context, PLATFORM

if PLATFORM == "unix":
    from zugbruecke.core.errors import WineError

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.skipif(PLATFORM != "unix", reason="only relevant for unix side")
@pytest.mark.parametrize(
    "arch,conv,ctypes,dll_path", get_context(__file__, handle=False)
)
def test_path_unix_to_wine_abs(arch, conv, ctypes, dll_path):

    PATH_A = ("/foo/bar", "Z:\\foo\\bar")
    assert ctypes.zb_path_unix_to_wine(PATH_A[0]) == PATH_A[1]


@pytest.mark.skipif(PLATFORM != "unix", reason="only relevant for unix side")
@pytest.mark.parametrize(
    "arch,conv,ctypes,dll_path", get_context(__file__, handle=False)
)
def test_path_unix_to_wine_rel(arch, conv, ctypes, dll_path):

    PATH_A = ("foo/bar", "foo\\bar")
    path_out = ctypes.zb_path_unix_to_wine(PATH_A[0])
    assert path_out[:3] == "Z:\\"
    assert path_out.endswith(PATH_A[1])
    assert len(path_out) > len(PATH_A[1]) + len("Z:\\")


@pytest.mark.skipif(PLATFORM != "unix", reason="only relevant for unix side")
@pytest.mark.parametrize(
    "arch,conv,ctypes,dll_path", get_context(__file__, handle=False)
)
def test_path_wine_to_unix_abs(arch, conv, ctypes, dll_path):

    PATH_A = "C:\\"
    path_out = ctypes.zb_path_wine_to_unix(PATH_A)
    assert path_out.startswith("/")
    assert path_out.endswith("/c:/")
    assert len(path_out) > len("/") + len("/c:/")


@pytest.mark.skipif(PLATFORM != "unix", reason="only relevant for unix side")
@pytest.mark.parametrize(
    "arch,conv,ctypes,dll_path", get_context(__file__, handle=False)
)
def test_path_wine_to_unix_fail(arch, conv, ctypes, dll_path):

    PATH_A = "a" * 270
    with pytest.raises(WineError):
        _ = ctypes.zb_path_wine_to_unix(PATH_A)
