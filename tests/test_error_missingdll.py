# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/test_error_missingdll.py: Checks for proper error handling if DLL does not exist

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

from .lib.ctypes import get_context

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@pytest.mark.parametrize(
    "arch,conv,ctypes,dll_path", get_context(__file__, handle=False)
)
def test_missingdll(arch, conv, ctypes, dll_path):

    missing_path = "tests/nonexistent_%s_%s.dll" % (conv, arch)

    with pytest.raises(OSError):
        dll = getattr(ctypes, conv).LoadLibrary(missing_path)


@pytest.mark.parametrize(
    "arch,conv,ctypes,dll_path", get_context(__file__, handle=False)
)
def test_missingdll_attr(arch, conv, ctypes, dll_path):

    missing_attr = "nonexistent_%s_%s_attr" % (conv, arch)

    with pytest.raises(OSError):
        dll = getattr(ctypes.cdll, missing_attr)


# def test_missingdll_oledll(): # TODO
#
# 	with pytest.raises(OSError):
# 		dll = ctypes.oledll.LoadLibrary('tests/nonexistent3_dll.dll')

# def test_missingdll_oledll_attr(): # TODO
#
# 	with pytest.raises(OSError):
# 		dll = ctypes.oledll.nonexistent33_dll
