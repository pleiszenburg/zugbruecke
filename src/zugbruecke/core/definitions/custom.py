# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/definitions/simple.py: Simple argument definition

    Required to run on platform / side: [UNIX, WINE]

    Copyright (C) 2017-2023 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
from typing import Any, Dict, List, Optional, Tuple, Union

from ..abc import CacheABC, DefinitionABC
from ..const import CUSTOM_GROUP
from ..typeguard import typechecked

from . import base

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class DefinitionCustom(base.Definition):

    GROUP = CUSTOM_GROUP

    def __init__(self, *args: Any, **kwargs: Any):

        super().__init__(*args, **kwargs)

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
        }

    @classmethod
    def from_packed(cls,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: Optional[str], # t
    ) -> DefinitionABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        base_type, data_type = cls._assemble_datatype(type_name, flags)

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = type_name,
            data_type = data_type,
            base_type = base_type,
        )

    @classmethod
    def _assemble_datatype(cls, type_name: Optional[str], flags: List[int]) -> Tuple[Any, Any]:
        """
        Assemble ctypes data type

        Counterpart to `_disassemble_datatype`
        """

        base_type = ctypes.c_void_p  # use void pointer as place holder type
        if len(flags) > 0:
            raise ValueError('flags unsupported for custom data types')
        data_type = base_type

        return base_type, data_type

    @classmethod
    def _from_data_type(
        cls,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: Optional[str], # t
        data_type: Any,
        base_type: Any,
        cache: CacheABC,
    ):
        """
        Simple group-specific helper for from ctypes data type
        """

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = type_name,
            data_type = data_type,
            base_type = base_type,
        )
