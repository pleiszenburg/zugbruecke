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
from sys import platform
from platform import architecture

from wenv import EnvConfig

from .const import ARCHS, CONVENTIONS, PYTHONBUILDS_FN
from .names import get_dll_path
from .pythonversion import read_python_builds

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT / PLATFORM
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ARCHITECTURE = architecture()[0][:2]

if any([platform.startswith(os_name) for os_name in ["linux", "darwin", "freebsd"]]):

    import zugbruecke
    cfg = EnvConfig()
    builds = read_python_builds(fn = os.path.join(cfg['prefix'], PYTHONBUILDS_FN))

    CTYPES = {
        arch: [
            zugbruecke.CtypesSession(arch=arch, pythonversion=build)
            for build in builds[arch]
        ] for arch in ARCHS
    }
    PLATFORM = "unix"

elif platform.startswith("win"):

    import ctypes as _ctypes
    from ctypes import util

    _ctypes.util = util

    CTYPES = {
        arch: [_ctypes]
        for arch in ARCHS if arch[3:] == ARCHITECTURE
    }
    PLATFORM = "wine"

else:

    raise SystemError("unsopported platform")

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_dll_handle(arch, ctypes_build, convention, test_fn):
    "get handle to dll for given arch and convention"

    try:
        return getattr(ctypes_build, convention).LoadLibrary(
            get_dll_path(
                arch, convention, test_fn
            )  # TODO this will parse setup.cfg on EVERY call
        )
    except:
        raise SystemError(
            "Ups!",
            arch,
            convention,
            test_fn,
            get_dll_path(arch, convention, test_fn),
            os.getcwd(),
        )


def get_context(test_path: str, handle: bool = True):
    """all archs and conventions,
    either test dll handle or path is provided
    """

    test_fn = os.path.basename(test_path)

    for convention in CONVENTIONS:
        for arch in ARCHS:
            for ctypes_build in CTYPES.get(arch, tuple()):
                if PLATFORM == "unix" or arch[3:] == ARCHITECTURE:
                    if handle:
                        yield (
                            arch,
                            convention,
                            ctypes_build,
                            get_dll_handle(arch, ctypes_build, convention, test_fn),
                        )
                    else:
                        yield (
                            arch,
                            convention,
                            ctypes_build,
                            get_dll_path(arch, convention, test_fn),
                        )
