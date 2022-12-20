# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/definitions/memsync.py: Memsync definitions

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
from typing import Any, Dict, List, Optional, Union

from ..abc import CacheABC, DefinitionMemsyncABC
from ..typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class DefinitionMemsync(DefinitionMemsyncABC):
    """
    Represent the definition of a block of memory to be kept in sync
    """

    def __init__(
        self,
        cache: CacheABC,
        pointer: List[Union[int, str]],  # "p"
        length: Optional[List[Union[int, str]]] = None,  # "l"
        type: str = "c_ubyte",  # "t" - type
        null: bool = False,  # "n" - null-terminated string
        unic: bool = False,  # "w" - handle unicode
        custom: Optional[Any] = None,  # "_c" - custom data type classes
        func: Optional[str] = None,  # "f" - compile length function
    ):

        self._pointer = pointer
        self._length = length
        self._type = type
        self._null = null
        self._unic = unic
        self._custom = custom
        self._func = func

        if self._func is not None:
            self._func_callable = eval(self._func)  # "_f" - HACK?

        self._type_cls = getattr(ctypes, self._type, None)  # "_t"
        if self._type_cls is None:
            _, self._type_cls = cache.struct[self._type]

        self._size = ctypes.sizeof(self._type_cls)  # "s"

    def __repr__(self) -> str:

        return f'<Memsync type={self._type} null={self._null} unic={self._unic} func={self._func is not None}>'

    def as_packed(self) -> Dict:
        """
        Pack as dict so it can be sent to other side

        Counterpart to `from_packed`
        """

        return {
            'pointer': self._pointer,
            'length': self._length,
            'type': self._type,
            'null': self._null,
            'unic': self._unic,
            'func': self._func,
        }

    @classmethod
    def from_packed(cls, packed: Dict, cache: CacheABC) -> DefinitionMemsyncABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        return cls(**packed, cache = cache)

    @classmethod
    def from_raw(cls, definition: Dict, cache: CacheABC) -> DefinitionMemsyncABC:
        """
        Ingest raw definition given by user
        """

        # Compatibility with older versions of zugbruecke TODO deprecated
        if 'p' in definition.keys():
            definition['pointer'] = definition.pop('p')
        if 'l' in definition.keys():
            definition['length'] = definition.pop('l')
        if 't' in definition.keys():
            definition['type'] = definition.pop('t')
        if 'n' in definition.keys():
            definition['null'] = definition.pop('n')
        if 'w' in definition.keys():
            definition['unic'] = definition.pop('w')
        if '_c' in definition.keys():
            definition['custom'] = definition.pop('_c')
        if 'f' in definition.keys():
            definition['func'] = definition.pop('f')

        return cls(**definition, cache = cache)

    @classmethod
    def from_raws(cls, definitions: List[Dict], cache: CacheABC) -> List[DefinitionMemsyncABC]:
        """
        Ingest raw definitions given by user
        """

        return [cls.from_raw(definition, cache = cache) for definition in definitions]
