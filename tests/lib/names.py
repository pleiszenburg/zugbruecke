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
from typing import List

from toml import loads
from typeguard import typechecked

from .const import DLL_FLD

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def get_dll_fn(arch: str, convention: str, fn: str) -> str:
    """
    get name & path of test dll for given arch and convention

    Args:
        - arch: Architecture of DLL
        - convention: Calling convention
        - fn: File name of Python source file
    Returns:
        DLL file name
    """

    assert fn.lower().endswith(".py")
    name = fn[:-3]

    return "{NAME:s}_{CONVENTION:s}-{ARCH:s}.dll".format(
        NAME=name,
        CONVENTION=convention,
        ARCH=arch,
    )


@typechecked
def get_dll_path(arch: str, convention: str, fld: str, fn: str) -> str:
    """
    get path to dll for given arch and convention

    Args:
        - arch: Architecture
        - convention: Calling convention
        - fld: root, either tests or benchmark
        - fn: File name of Python source file
    Returns:
        Path to DLL file
    """

    return os.path.join(
        fld,
        DLL_FLD,
        get_dll_fn(arch, convention, fn),
    )


@typechecked
def get_benchmark_fld(abspath: bool = True) -> str:
    """
    get full path of benchmark folder

    Args:
        - abspath: Require absolute path
    Returns:
        Path to benchmark
    """

    if not abspath:
        return 'benchmark'

    return os.path.join(os.path.abspath(os.getcwd()), 'benchmark')


@typechecked
def get_benchmark_fns(fld: str) -> List[str]:
    """
    get list of Python benchmark files in project benchmark folder

    Args:
        - fld: Path to directory containing Python benchmark code files
    Returns:
        List of file names
    """

    fns = []

    for entry in os.listdir(fld):
        if not entry.lower().endswith(".py"):
            continue
        if entry.lower().startswith("_"):
            continue
        if not os.path.isfile(os.path.join(fld, entry)):
            continue
        fns.append(entry)

    return fns


@typechecked
def get_test_fld(abspath: bool = True) -> str:
    """
    get full path of project test folder

    Args:
        - abspath: Require absolute path
    Returns:
        Path to test folder
    """

    cwd = os.path.abspath(os.getcwd())
    fld = None

    if not os.path.isfile("pyproject.toml"):
        raise FileNotFoundError("pyproject.toml configuration file missing in cwd")

    with open('pyproject.toml', mode = 'r', encoding = 'utf-8') as f:
        pyproject = loads(f.read())

    fld = pyproject['tool']['pytest']['ini_options']['testpaths'][0]

    if abspath:
        fld = os.path.join(cwd, fld)

    if not os.path.isdir(fld):
        raise ValueError(
            '"testpaths" in "pyproject.toml" does not point to an existing directory'
        )

    return fld


@typechecked
def get_test_fns(fld: str) -> List[str]:
    """
    get list of Python test files in project test folder

    Args:
        - fld: Path to directory containing Python test code files
    Returns:
        List of file names
    """

    fns = []

    for entry in os.listdir(fld):
        if not entry.lower().endswith(".py"):
            continue
        if not entry.lower().startswith("test_"):
            continue
        if not os.path.isfile(os.path.join(fld, entry)):
            continue
        fns.append(entry)

    return fns