# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/definition_struct.py: Struct argument definition

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
from typing import Any, Dict, List, Union, Tuple

from ..abc import CacheABC, DefinitionABC
from ..typeguard import typechecked

from . import definition_base as base

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class DefinitionStruct(base.Definition):

    GROUP = "PyCStructType"

    def __init__(self,
        *args: Any,
        fields: List[DefinitionABC],
        **kwargs: Any,
    ):

        super().__init__(*args, **kwargs)
        self._fields = fields

    def as_packed(self) -> Dict:
        """
        Pack as dict so it can be sent to other side

        Counterpart to `from_packed`
        """

        return {
            "group": self.GROUP,
            "flags": self._flags,
            "field_name": self._field_name,
            "type_name": self._type_name,
            "fields": [field.as_packed() for field in self._fields],
        }

    @classmethod
    def from_packed(cls,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: str, # t
        fields: List[Dict],
        cache: CacheABC,
    ) -> DefinitionABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        fields = [base.Definition.from_packed(field, cache = cache) for field in fields]

        type_name = f'struct_{hash(tuple((field.field_name, field.data_type) for field in fields)):x}'
        try:
            base_type, data_type = cache.struct[type_name]
        except KeyError:
            base_type, data_type = cls._assemble_datatype(type_name, flags, fields)
            cache.struct[type_name] = base_type, data_type

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = type_name,
            data_type = data_type,
            base_type = base_type,
            fields = fields,
        )

    @classmethod
    def _assemble_datatype(cls, type_name: str, flags: List[int], fields: List[DefinitionABC]) -> Tuple[Any, Any]:
        """
        Assemble ctypes data type

        Counterpart to `_disassemble_datatype`
        """

        base_type = type(
            type_name,  # Potenial BUG: in __main__ scope, problematic?
            (ctypes.Structure,),
            {"_fields_": [(field.field_name, field.data_type) for field in fields]},
        )
        data_type = cls._apply_flags(base_type, flags)

        return base_type, data_type

    @classmethod
    def _from_data_type(
        cls,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: str, # t
        data_type: Any,
        base_type: Any,
        cache: CacheABC,
    ):
        """
        Struct group-specific helper for from ctypes data type
        """

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = type_name,
            data_type = data_type,
            base_type = base_type,
            fields = [
                cls.from_data_type(
                    data_type = field[1],
                    field_name = field[0],
                    cache = cache,
                ) for field in base_type._fields_
            ],
            cache = cache,
        )
