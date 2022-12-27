# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/const.py: Holds constant values, flags, types

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
# IMPORT / PLATFORM
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from platform import architecture
from sys import platform

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ARCHITECTURE = architecture()[0][:2]

if any([platform.startswith(os_name) for os_name in ["linux", "darwin", "freebsd"]]):
    PLATFORM = "unix"
elif platform.startswith("win"):
    PLATFORM = "wine"
else:
    raise SystemError("unsopported platform")

HEADER_FN = "tmp_header.h"
SOURCE_FN = "tmp_source.c"

DLL_FLD = "dlls"

DLL_HEADER = """

#ifndef TESTDLL_H
#define TESTDLL_H

#include <stdio.h>
#include <windows.h>
#include <stdint.h>
#include <float.h>
#include <limits.h>
#include <math.h>

typedef int32_t bool;
#define TRUE 1
#define FALSE 0

{{ HEADER }}

#endif

"""

DLL_SOURCE = """

#include "{{ HEADER_FN }}"

{{ SOURCE }}

"""

ARCHS = ["win32", "win64"]
CONVENTIONS = ["cdll", "windll"]

PREFIX = {
    "cdll": "__declspec(dllexport)",
    "windll": "__declspec(dllexport)",
}
SUFFIX = {
    "cdll": "__cdecl",
    "windll": "__stdcall",
}

CC = {
    "win32": "i686-w64-mingw32-gcc",
    "win64": "x86_64-w64-mingw32-gcc",
}
_CFLAGS = ["-Wall", "-shared", "-std=c99"]
CFLAGS = {
    "cdll": _CFLAGS + ["-Wl,--subsystem,windows"],
    "windll": _CFLAGS + ["-Wl,-add-stdcall-alias"],
}
LDFLAGS = [
    "-lm",
]

PYTHONBUILDS_FN = 'pythonbuilds.json'

PYTHON_MINOR_MIN = 7
PYTHON_MINOR_MAX = 11
