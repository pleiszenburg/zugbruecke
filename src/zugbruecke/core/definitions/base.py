# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/definitions/base.py: Base argument definition

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
from typing import Any, Dict, List, Optional, Tuple, Union

from ..abc import CacheABC, DefinitionABC
from ..const import FLAG_POINTER
from ..errors import DataFlagError
from ..typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Definition(DefinitionABC):
    """
    Represent the definition of a function argument or return type
    """

    GROUP = None

    def __init__(self,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: Optional[str], # t
        data_type: Any,
        base_type: Any,
    ):

        self._flags = flags
        self._field_name = field_name
        self._type_name = type_name

        self._data_type = data_type
        self._base_type = base_type

    def __repr__(self) -> str:

        return f'<Definition group={self.GROUP} field={self._field_name} type={self._type_name} flags={self._flags}>'  # TODO

    @property
    def flags(self) -> List[int]:

        return self._flags

    @property
    def data_type(self) -> Any:
        """
        The actual ctypes data type (all flags applied)
        """

        return self._data_type

    @property
    def base_type(self) -> Any:
        """
        Base ctypes data type (no flags applied)
        """

        return self._base_type

    @property
    def field_name(self) -> Union[str, int, None]:
        """
        Relevant if definition is part of a struct
        """

        return self._field_name

    @property
    def type_name(self) -> Optional[str]:
        """
        Relevant to access cached types
        """

        return self._type_name

    @property
    def array_depth(self) -> int:  # "d"
        """
        Number of array flags (i.e. "dimensions")
        """

        return len([flag for flag in self._flags if flag > 0])

    @property
    def is_pointer(self) -> bool:  # "p"
        """
        Flags contain at least one pointer flag
        """

        return len([flag for flag in self._flags if flag == FLAG_POINTER]) > 0

    @property
    def is_scalar(self) -> bool:  # "s"
        """
        Flags do not contain array flag
        """

        return self.array_depth == 0

    @property
    def is_void(self) -> bool:
        """
        Indicate minimal void pointer, no flags, no array, likely handled by memsync
        """

        return self._data_type == ctypes.c_void_p and not self.is_pointer and self.is_scalar

    @staticmethod
    def _apply_flags(data_type: Any, flags: List[int]) -> Any:
        """
        Apply flags, i.e. pointer and array, to ctypes data type
        """

        for flag in reversed(flags):
            if flag > 0:  # array
                data_type = data_type * flag
            elif flag == FLAG_POINTER:
                data_type = ctypes.POINTER(data_type)
            else:
                raise DataFlagError(f'unknown non-pointer flag for array "{flag:d}"')

        return data_type

    @classmethod
    def _assemble_datatype(cls, type_name: Optional[str], flags: List[int]) -> Tuple[Any, Any]:
        """
        Assemble ctypes data type

        Counterpart to `_disassemble_datatype`
        """

        raise NotImplementedError()

    @staticmethod
    def _disassemble_datatype(data_type: Any) -> Tuple[Any, Union[str, None], str, List[int]]:
        """
        Disassemble ctypes data type into base type, name, group and flags

        Counterpart to `_assemble_datatype`
        """

        flags = []

        base_type = data_type
        type_name = getattr(base_type, "__name__", None)
        group = type(base_type).__name__

        while group in ("PyCPointerType", "PyCArrayType"):

            flags.append(FLAG_POINTER if group == "PyCPointerType" else base_type._length_)

            base_type = base_type._type_
            type_name = getattr(base_type, "__name__", None)  # TODO Is there a case without a name?
            group = type(base_type).__name__

        return base_type, type_name, group, flags

    @classmethod
    def _from_data_type(cls, **kwargs: Any):
        """
        Group-specific helper for from ctypes data type
        """

        raise NotImplementedError()

    def as_packed(self) -> Dict:
        """
        Pack as dict so it can be sent to other side

        Counterpart to `from_packed`
        """

        raise NotImplementedError()

    @classmethod
    def from_packed(cls, packed: Dict, cache: CacheABC) -> DefinitionABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        from .simple import DefinitionSimple
        from .struct import DefinitionStruct
        from .func import DefinitionFunc

        group = packed.pop("group")

        if group == DefinitionSimple.GROUP:
            return DefinitionSimple.from_packed(**packed)

        if group == DefinitionStruct.GROUP:
            return DefinitionStruct.from_packed(**packed, cache = cache)

        if group == DefinitionFunc.GROUP:
            return DefinitionFunc.from_packed(**packed, cache = cache)

        raise ValueError(f'unknown group "{group}"')  # TODO new error type?

    @classmethod
    def from_data_types(
        cls,
        cache: CacheABC,
        data_types: List[Any],
    ) -> List[DefinitionABC]:

        return [cls.from_data_type(data_type = data_type, cache = cache) for data_type in data_types]

    @classmethod
    def from_data_type(
        cls,
        cache: CacheABC,
        data_type: Any,
        field_name: Union[str, int, None] = None,
    ) -> DefinitionABC:
        """
        type_name: Name of datatype, such as c_int, if there is one, else None
        group: 'PyCSimpleType', 'PyCStructType', 'PyCArrayType' or 'PyCPointerType'
        flags: Pointer flag or length of array (one entry per dimension)
        """

        from .simple import DefinitionSimple
        from .struct import DefinitionStruct
        from .func import DefinitionFunc
        from .custom import DefinitionCustom

        base_type, type_name, group, flags = cls._disassemble_datatype(data_type)

        kwargs = dict(
            data_type = data_type,
            base_type = base_type,
            type_name = type_name,
            flags = flags,
            field_name = field_name,
            cache = cache,
        )

        if group == DefinitionSimple.GROUP:
            return DefinitionSimple._from_data_type(**kwargs)

        if group == DefinitionStruct.GROUP:
            return DefinitionStruct._from_data_type(**kwargs)

        if group == DefinitionFunc.GROUP:
            return DefinitionFunc._from_data_type(**kwargs)

        if hasattr(data_type, 'from_param'):
            return DefinitionCustom._from_data_type(**kwargs)

        raise ValueError(f'unknown group "{group}"')  # TODO new error type?
