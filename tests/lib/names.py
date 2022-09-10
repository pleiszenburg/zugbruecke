# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/names.py: Processing for test and DLL names

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

import os

from toml import loads

from .const import DLL_FLD

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_dll_fn(arch, convention, test_fn, custom=None):
    "get name & path of test dll for given arch and convention"

    assert test_fn.lower().endswith(".py")
    name = test_fn[:-3]

    return "{NAME:s}_{CONVENTION:s}-{ARCH:s}{CUSTOM:s}.dll".format(
        NAME=name,
        CONVENTION=convention,
        ARCH=arch,
        CUSTOM=("-" + custom) if custom is not None else "",
    )


def get_dll_path(arch, convention, test_fn, custom=None):
    "get name & path of test dll for given arch and convention RELATIVE TO CWD"

    return os.path.join(
        get_test_fld(abspath=False),
        DLL_FLD,
        get_dll_fn(arch, convention, test_fn, custom=custom),
    )


def get_test_fld(abspath=True):
    "get full path of project test folder"

    cwd = os.path.abspath(os.getcwd())
    test_fld = None

    if not os.path.isfile("pyproject.toml"):
        raise FileNotFoundError("pyproject.toml configuration file missing in cwd")

    with open('pyproject.toml', mode = 'r', encoding = 'utf-8') as f:
        pyproject = loads(f.read())

    test_fld = pyproject['tool']['pytest']['ini_options']['testpaths'][0]

    if abspath:
        test_fld = os.path.join(cwd, test_fld)

    if not os.path.isdir(test_fld):
        raise ValueError(
            '"testpaths" in "pyproject.toml" does not point to an existing directory'
        )

    return test_fld
