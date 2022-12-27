# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/definitions/func.py: Func argument definition

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
from ctypes import _FUNCFLAG_CDECL
from typing import Any, Dict, List, Optional, Tuple, Union

from ..abc import CacheABC, DefinitionABC, DefinitionMemsyncABC
from ..const import _FUNCFLAG_STDCALL, FUNC_GROUP
from ..typeguard import typechecked

from . import base
from . import memsync as ms

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class DefinitionFunc(base.Definition):

    GROUP = FUNC_GROUP

    def __init__(self,
        *args: Any,
        argtypes: List[DefinitionABC],
        restype: DefinitionABC,
        memsyncs: List[DefinitionMemsyncABC],
        func_flags: int,
        **kwargs: Any,
    ):

        super().__init__(*args, **kwargs)
        self._argtypes = argtypes
        self._restype = restype
        self._memsyncs = memsyncs
        self._func_flags = func_flags

    @property
    def argtypes(self) -> List[DefinitionABC]:

        return self._argtypes

    @property
    def restype(self) -> DefinitionABC:

        return self._restype

    @property
    def memsyncs(self) -> List[DefinitionMemsyncABC]:

        return self._memsyncs

    @property
    def func_flags(self) -> int:

        return self._func_flags

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
            "argtypes": [argtype.as_packed() for argtype in self._argtypes],
            "restype": self._restype.as_packed(),
            "memsyncs": [item.as_packed() for item in self._memsyncs],
            "func_flags": self._func_flags
        }

    @classmethod
    def from_packed(cls,
        flags: List[int], # f
        field_name: Union[str, int, None], # n
        type_name: str, # t
        argtypes: List[Dict],
        restype: Dict,
        memsyncs: List[Dict],
        func_flags: int,
        cache: CacheABC,
    ) -> DefinitionABC:
        """
        Unpack from dict received from other side

        Counterpart to `as_packed`
        """

        argtypes = [base.Definition.from_packed(argtype, cache = cache) for argtype in argtypes]
        restype = base.Definition.from_packed(restype, cache = cache)
        memsyncs = [ms.DefinitionMemsync.from_packed(item, cache = cache) for item in memsyncs]

        conv = _FUNCFLAG_STDCALL if (func_flags & _FUNCFLAG_STDCALL) else _FUNCFLAG_CDECL

        try:
            base_type, data_type = cache.by_conv(conv)[type_name]
        except KeyError:
            base_type, data_type = cls._assemble_datatype(
                type_name = type_name,
                argtypes = argtypes,
                flags = flags,
                restype = restype,
                memsyncs = memsyncs,
                func_flags = func_flags,
                cache = cache,
            )
            cache.by_conv(conv)[type_name] = base_type, data_type

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = type_name,
            data_type = data_type,
            base_type = base_type,
            argtypes = argtypes,
            restype = restype,
            memsyncs = memsyncs,
            func_flags = func_flags,
        )

    @classmethod
    def _assemble_datatype(
        cls,
        type_name: str,
        flags: List[int],
        argtypes: List[DefinitionABC],
        restype: DefinitionABC,
        memsyncs: List[DefinitionMemsyncABC],
        func_flags: int,
        cache: CacheABC,
    ) -> Tuple[Any, Any]:
        """
        Assemble ctypes data type

        Counterpart to `_disassemble_datatype`
        """

        class PyCFuncPtrType(type(ctypes._CFuncPtr)):  # name of meta class is important, later used as group name
            @property
            def memsync(cls):
                return getattr(cls, '_memsync_', [])
            @memsync.setter
            def memsync(cls, value: List[Dict]):
                if not isinstance(value, list):
                    TypeError('memsync attr must be a list')
                setattr(cls, '_memsync_', ms.DefinitionMemsync.from_raws(value, cache))

        base_type = PyCFuncPtrType(
            type_name,
            (ctypes._CFuncPtr,),
            {
                "_argtypes_": [argtype.data_type for argtype in argtypes],
                "_restype_": restype.data_type,
                "_memsync_": memsyncs,
                "_flags_": func_flags,
            },
        )
        data_type = cls._apply_flags(base_type, flags)

        return base_type, data_type

    @staticmethod
    def _make_type_name(restype: Any, argtypes: List[Any], func_flags: int) -> str:

        return f'functype_{hash((restype, tuple(argtypes), func_flags)):x}'

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
        Func group-specific helper for from ctypes data type
        """

        return cls(
            flags = flags,
            field_name = field_name,
            type_name = cls._make_type_name(base_type._restype_, base_type._argtypes_, base_type._flags_),
            data_type = data_type,
            base_type = base_type,
            argtypes = cls.from_data_types(data_types = base_type._argtypes_, cache = cache),
            restype = cls.from_data_type(data_type = base_type._restype_, cache = cache),
            memsyncs = base_type.memsync,  # already parsed into definition via meta class
            func_flags = base_type._flags_,
        )

    @classmethod
    def generate_callback_decorator(
        cls,
        cache: CacheABC,
        func_flags: int,
        restype: Any,
        argtypes: List[Any],
    ) -> Any:
        """
        Used by CFUNCTYPE and WINFUNCTYPE
        """

        type_name = cls._make_type_name(restype, argtypes, func_flags)
        conv = _FUNCFLAG_STDCALL if (func_flags & _FUNCFLAG_STDCALL) else _FUNCFLAG_CDECL

        try:
            base_type, data_type = cache.by_conv(conv)[type_name]
        except KeyError:
            base_type, data_type = cls._assemble_datatype(
                type_name = type_name,
                argtypes =  base.Definition.from_data_types(cache = cache, data_types = argtypes),
                flags = [],  # no flags available
                restype = base.Definition.from_data_type(cache = cache, data_type = restype),
                memsyncs = [],  # no memsync available
                func_flags = func_flags,
                cache = cache,
            )
            cache.by_conv(conv)[type_name] = base_type, data_type

        return data_type
