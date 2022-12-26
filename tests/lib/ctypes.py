# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/ctypes.py: Offers handles on ctypes/zugbruecke sessions and DLLs

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
from typing import Any, Union

from typeguard import typechecked
from wenv import EnvConfig

from .const import ARCHITECTURE, ARCHS, CONVENTIONS, PLATFORM, PYTHONBUILDS_FN
from .names import get_dll_path, get_test_fld
from .pythonversion import read_python_builds

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT / PLATFORM
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if PLATFORM == "unix":

    import zugbruecke
    cfg = EnvConfig()
    builds = read_python_builds(fn = os.path.join(cfg['prefix'], PYTHONBUILDS_FN))

    CTYPES = {
        arch: [
            zugbruecke.CtypesSession(arch=arch, pythonversion=build)
            for build in builds[arch]
        ] for arch in ARCHS
    }

elif PLATFORM == "wine":

    import ctypes as _ctypes
    from ctypes import util

    _ctypes.util = util

    CTYPES = {
        arch: [_ctypes]
        for arch in ARCHS if arch[3:] == ARCHITECTURE
    }

else:

    raise SystemError("unsopported platform")

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def get_dll_handle(arch: str, ctypes: Any, convention: str, fld: str, fn: str) -> Any:
    """
    get handle to dll for given arch and convention

    Args:
        - arch: Architecture
        - ctypes: zugbruecke ctypes session or original ctypes
        - convention: Calling convention
        - fld: root, either tests or benchmark
        - fn: File name of Python source file
    Returns:
        Handle on DLL file
    """

    path = get_dll_path(arch, convention, fld, fn)

    try:
        return getattr(ctypes, convention).LoadLibrary(path)
    except Exception as e:
        raise SystemError(
            "failed to attach to DLL file",
            arch,
            convention,
            path,
            os.getcwd(),
        ) from e


@typechecked
def get_context(fn: str, handle: bool = True) -> Union[Any, str]:
    """
    all archs and conventions, either test dll handle or path is provided

    Args:
        - fn: File name of Python source file
        - handle: Return handle on DLL (or just its path)
    Yields:
        DLL handles (or paths) per calling convention, architecture and wenv Python version
    """

    fn = os.path.basename(fn)
    fld = get_test_fld(abspath=False)

    for convention in CONVENTIONS:
        for arch in ARCHS:
            for ctypes_build in CTYPES.get(arch, tuple()):
                if PLATFORM == "unix" or arch[3:] == ARCHITECTURE:
                    if handle:
                        yield (
                            arch,
                            convention,
                            ctypes_build,
                            get_dll_handle(
                                arch,
                                ctypes_build,
                                convention,
                                fld,
                                fn,
                            ),
                        )
                    else:
                        yield (
                            arch,
                            convention,
                            ctypes_build,
                            get_dll_path(
                                arch,
                                convention,
                                fld,
                                fn,
                            ),
                        )
