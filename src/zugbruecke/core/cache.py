# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/cache.py: Cached types and handles

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

from ctypes import _FUNCFLAG_CDECL
from typing import Dict

from .abc import CacheABC
from .const import _FUNCFLAG_STDCALL
from .typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Cache(CacheABC):
    """
    Holding struct types, function types and function handles
    """

    def __init__(self):

        self._cdecl = {}
        self._stdcall = {}
        self._struct = {}
        self._handle = {}

    @property
    def cdecl(self) -> Dict:

        return self._cdecl

    @property
    def stdcall(self) -> Dict:

        return self._stdcall

    @property
    def struct(self) -> Dict:

        return self._struct

    @property
    def handle(self) -> Dict:

        return self._handle

    def by_conv(self, flag: int) -> Dict:
        """
        By calling convention flag
        """

        if flag == _FUNCFLAG_CDECL:
            return self._cdecl

        if flag == _FUNCFLAG_STDCALL:
            return self._stdcall

        raise ValueError(f'unknown flag "{flag}"')
