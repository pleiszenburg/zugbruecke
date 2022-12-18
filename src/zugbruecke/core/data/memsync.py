# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/memsync.py: Memsync definitions

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

import ctypes
from typing import Dict, List, Optional

from ..abc import MemsyncABC
from ..typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

CACHE = {}  # TODO struct types by name

@typechecked
class Memsync(MemsyncABC):

    def __init__(
        self,
        type: str = "c_ubyte",  # "t" - defaut type
        null: bool = False,  # "n" - null-terminated string
        unic: bool = False,  # "w" - handle unicode
        func: Optional[str] = None,  # "f" - compile length function
    ):

        self._type = type
        self._null = null
        self._unic = unic
        self._func = func

        if self._func is not None:
            self._func_callable = eval(self._func)  # "_f" - HACK?

        self._type_cls = getattr(ctypes, self._type, None)  # "_t"
        if self._type_cls is None:
            self._type_cls = CACHE[self._type]

        self._size = ctypes.sizeof(self._type_cls)  # "s"

    def as_packed(self) -> Dict:
        """
        Pack as dict so it can be sent to other side

        Counterpart to `from_packed`
        """

        return {
            'type': self._type,
            'null': self._null,
            'unic': self._unic,
            'func': self._func,
        }

    @classmethod
    def from_packed(cls, packed: Dict) -> MemsyncABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        return cls(**packed)

    @classmethod
    def from_dict(cls, definition: Dict) -> MemsyncABC:
        """
        Ingest definition given by user
        """

        return cls(**definition)

    @classmethod
    def from_dicts(cls, definitions: List[Dict]) -> List[MemsyncABC]:
        """
        Ingest definitions given by user
        """

        return [Memsync.from_dict(definition) for definition in definitions]
