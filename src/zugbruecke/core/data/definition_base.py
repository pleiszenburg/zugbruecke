# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/definition_base.py: Base argument definition

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

from ..abc import DefinitionABC
from ..const import FLAG_POINTER
from ..errors import DataFlagError
from ..typeguard import typechecked

from . import definition_simple as simple
from . import definition_struct as struct
from . import definition_func as func

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Definition(DefinitionABC):
    """
    Represent the definition of a function argument or return type
    """

    group = None

    data_type_cache = {} # TODO
    base_type_cache = {} # TODO

    def __init__(self,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: str, # t
        data_type: Any,
        base_type: Any,
    ):

        self._flags = flags
        self._field_name = field_name
        self._type_name = type_name

        self._data_type = data_type
        self._base_type = base_type

        # # HACK Different struct types from different name spaces can have identical names
        # _type_name = "{TYPE_NAME:s}@{ID:d}".format(TYPE_NAME = type_name, ID = id(datatype))
        #
        # # Keep track of datatype on client side
        # if _type_name not in DefinitionStruct.cache.keys():
        #     DefinitionStruct.cache[_type_name] = datatype

        # # Store the depth of arrays (arrays within arrays etc; for speed)
        # array_depth = len([flag for flag in flags if flag > 0]) # d
        # # Flag pure scalars as, well, pure scalars (for speed)
        # is_scalar = array_depth == 0 # s
        # # Flag elements containing pointers
        # contains_pointer = len([flag for flag in flags if flag == FLAG_POINTER]) != 0 # p

    def __repr__(self) -> str:

        return f'<Definition field={self._field_name} type={self._type_name} flags={self._flags}>'  # TODO

    @property
    def data_type(self) -> Any:

        return self._data_type

    @staticmethod
    def _apply_flags(data_type: Any, flags: List[int]) -> Any:
        """
        Apply flags, i.e. pointer and array, to ctypes data type
        """

        for flag in reversed(flags):
            if flag > 0:  # array
                data_type = data_type * flag
            elif flag == FLAG_POINTER:
                data_type = ctypes.POINTER(data_type) # TODO check for void pointer?
            else:
                raise DataFlagError("unknown non-pointer flag for array")

        return data_type

    @classmethod
    def _assemble_datatype(cls, type_name: str, flags: List[int]) -> Tuple[Any, Any]:
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
            type_name = base_type.__name__
            group = type(base_type).__name__

        return base_type, type_name, group, flags

    def as_packed(self) -> Dict:
        """
        Pack as dict so it can be sent to other side

        Counterpart to `from_packed`
        """

        raise NotImplementedError()

    @classmethod
    def from_packed(cls, packed: Dict) -> DefinitionABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        group = packed.pop("group")

        if group == simple.DefinitionSimple.GROUP:
            return simple.DefinitionSimple.from_packed(**packed)

        if group == struct.DefinitionStruct.GROUP:
            return struct.DefinitionStruct.from_packed(**packed)

        if group == func.DefinitionFunc.GROUP:
            return func.DefinitionFunc.from_packed(**packed)

        raise ValueError(f'unknown group "{group}"')  # TODO new error type?

    @classmethod
    def from_data_types(cls, data_types: List[DefinitionABC]) -> List[DefinitionABC]:

        return [cls.from_data_type(data_type) for data_type in data_types]

    @classmethod
    def from_data_type(cls, data_type: Any, field_name = None) -> DefinitionABC:
        """
        type_name: Name of datatype, such as c_int, if there is one, else None
        group: 'PyCSimpleType', 'PyCStructType', 'PyCArrayType' or 'PyCPointerType'
        flags: Pointer flag or length of array (one entry per dimension)
        """

        base_type, type_name, group, flags = cls._disassemble_datatype(data_type)

        kwargs = dict(
            data_type = data_type,
            base_type = base_type,
            type_name = type_name,
            flags = flags,
            field_name = field_name,
        )

        if group == simple.DefinitionSimple.GROUP:
            return simple.DefinitionSimple(**kwargs)

        if group == struct.DefinitionStruct.GROUP:
            return struct.DefinitionStruct(
                **kwargs,
                fields = [cls.from_data_type(field[1], field[0]) for field in base_type._fields_],
            )

        if group == func.DefinitionFunc.GROUP:
            kwargs["type_name"] = hash((base_type._restype_, base_type._argtypes_, base_type._flags_))
            return func.DefinitionFunc(
                **kwargs,
                argtypes_d = cls.from_data_types(base_type._argtypes_),
                restype_d = cls.from_data_type(base_type._restype_),
                memsync_d = Memsync.from_dicts(base_type.memsync),  # TODO
                func_flags = base_type._flags_,
            )

        raise ValueError(f'unknown group "{group}"')  # TODO new error type?
