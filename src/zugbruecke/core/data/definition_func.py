# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/definition_func.py: Func argument definition

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
from typing import Any, Dict, List, Tuple, Union

from ..abc import DefinitionABC, MemsyncABC
from ..typeguard import typechecked

from . import definition_base as base

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class DefinitionFunc(base.Definition):

    GROUP = "PyCFuncPtrType"

    def __init__(self,
        *args: Any,
        argtypes_d: List[DefinitionABC],
        restype_d: DefinitionABC,
        memsync_d: MemsyncABC,
        func_flags: int,
        **kwargs: Any,
    ):

        super().__init__(*args, **kwargs)
        self._argtypes_d = argtypes_d
        self._restype_d = restype_d
        self._memsync_d = memsync_d
        self._func_flags = func_flags

    def as_packed(self) -> Dict:
        """
        Pack as dict so it can be sent to other side

        Counterpart to `from_packed`
        """

        return {
            "group": self.group,
            "flags": self._flags,
            "field_name": self._field_name,
            "type_name": self._type_name,
            "argtypes_d": [argtype_d.as_packed() for argtype_d in self._argtypes_d],
            "restype_d": self._restype_d.as_packed(),
            "memsync_d": [item.as_packed() for item in self._memsync_d],
            "func_flags": self._func_flags
        }

    @classmethod
    def from_packed(cls,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: str, # t
        argtypes_d: List[Dict],
        restype_d: Dict,
        memsync_d: List[Dict],
        func_flags: int,
    ) -> DefinitionABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        argtypes_d = [base.Definition.from_packed(argtype_d) for argtype_d in argtypes_d]
        restype_d = base.Definition.from_packed(restype_d)
        memsync_d = [Memsync.from_packed(item) for item in memsync_d]  # TODO
        base_type, data_type = cls._assemble_datatype(type_name, flags, argtypes_d, restype_d, memsync_d, func_flags)

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = type_name,
            data_type = data_type,
            base_type = base_type,
            argtypes_d = argtypes_d,
            restype_d = restype_d,
            memsync_d = memsync_d,
            func_flags = func_flags,
        )

    @classmethod
    def _assemble_datatype(cls,
        type_name: str, flags: List[int],
        argtypes_d: List[DefinitionABC], restype_d: DefinitionABC, memsync_d: List[MemsyncABC],
        func_flags: int,
    ) -> Tuple[Any, Any]:
        """
        Assemble ctypes data type

        Counterpart to `_disassemble_datatype`
        """

        class base_type(ctypes._CFuncPtr):
            _argtypes_ = [argtype_d.data_type for argtype_d in argtypes_d]
            _restype_ = restype_d.data_type
            memsync = memsync_d
            _flags_ = func_flags

        data_type = cls._apply_flags(base_type, flags)

        return base_type, data_type
