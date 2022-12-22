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
from typing import Any, Dict, List, Optional, Tuple, Union

from ..abc import CacheABC, DefinitionMemsyncABC
from ..const import FLAG_POINTER, SIMPLE_GROUP, STRUCT_GROUP
from ..mempkg import Mempkg
from ..memory import (
    is_null_pointer,
    strip_pointer,
    strip_simplecdata,
)
from ..errors import DataMemsyncpathError
from ..typeguard import typechecked

from .base import Definition
from .struct import DefinitionStruct

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
        length: Optional[Union[ List[Union[int, str]], Tuple[List[Union[int, str]], ...] ]] = None,  # "l"
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

        self._func_callable = None if self._func is None else eval(self._func)  # "_f" HACK?

        self._type_cls = getattr(ctypes, self._type, None)  # "_t"
        if self._type_cls is None:
            self._type_cls, _ = cache.struct[self._type]  # access base type

        self._size = ctypes.sizeof(self._type_cls)  # "s"

    def __repr__(self) -> str:

        return f'<Memsync type={self._type} null={self._null} unic={self._unic} func={self._func is not None}>'

    @staticmethod
    def _get_str_len(ptr: Any, is_unicode: bool) -> int:
        """
        Get length of null-terminated string in bytes

        Args:
            - ptr: ctypes pointer to chars/wchars
            - is_unicode: flag indicating unicode characters
        Returns:
            Length in bytes
        """

        if is_unicode:
            datatype = ctypes.c_wchar
            datatype_p = ctypes.c_wchar_p
        else:
            datatype = ctypes.c_char
            datatype_p = ctypes.c_char_p

        return len(ctypes.cast(ptr, datatype_p).value) * ctypes.sizeof(datatype)

    def _get_arb_len(self, args: List[Any], retval: Optional[Any] = None) -> int:
        """
        Get length of arbitrary data

        Args:
            - args: Raw arguments
            - retval: Raw return value
        Returns:
            Length in bytes
        """

        # There is no function defining the length?
        if self._func is None:

            # Search for length
            length = self._get_item_by_path(
                self._length, args, retval
            )

            # Length might come from ctypes or a Python datatype
            return strip_simplecdata(length)

        # Make sure length can be computed from a tuple of arguments
        assert isinstance(self._length, tuple)

        # Compute length from arguments and return
        return self._func_callable(
            *(
                self._get_item_by_path(path, args, retval)
                for path in self._length
            )
        )

    @staticmethod
    def _get_item_by_path(
        path: List[Union[int, str]], args: List[Any], retval: Optional[Any] = None,
    ) -> Any:
        """
        Get (fragment of) argument or return value by path

        Args:
            - path: List of int and/or str describing (part of) an argument or return value
            - args: Raw arguments
            - retval: Raw return value
        Returns:
            Raw (fragment of) argument or return value
        """

        # Reference args_tuple as initial value
        element = args

        # Step through path
        for idx, segment in enumerate(path):

            # Element is an int
            if isinstance(segment, int):

                # Pointer to pointer (in top-level arguments) for memory allocation by DLL
                if segment < 0:
                    element = strip_pointer(element)

                # Dive into argument tuple
                else:
                    element = element[segment]

            # Element equals 'r' and index 0: Return value
            elif isinstance(segment, str) and idx == 0:

                if segment != "r":
                    raise DataMemsyncpathError(
                        'field with name (type string) is not return value ("r")'
                    )

                element = retval

                if element is None:
                    return None

            # Field name in struct
            elif isinstance(segment, str) and idx > 0:

                element = getattr(strip_pointer(element), segment)

            # TODO elements of arrays
            else:

                raise NotImplementedError("array elements can yet not be addressed")

        return element

    @staticmethod
    def _get_itemtype_by_path(
        path: List[Union[int, str]],
        argtypes: List[Definition],
        restype: Optional[Definition],
    ) -> Definition:
        """
        Get zugbruecke argtype or restype by path

        Args:
            - path: List of int and/or str describing (part of) an argument or return value
            - argtypes: zugbruecke argument types
            - restype: zugbruecke return type
        Returns:
            One zugbruecke argtype / restype definition
        """

        if isinstance(path[0], int):  # function argument
            itemtype = argtypes[path[0]]
        elif path[0] == "r":  # function return value
            itemtype = restype
        else:
            raise DataMemsyncpathError(
                f'path[0] is neither return value ("r") nor parameter (type int) "{path[0]}"'
            )

        # Step through path to argument type ...
        for segment in path[1:]:
            # Continue on special flags HACK
            if isinstance(segment, int) and segment < 0:
                continue
            # Go deeper ...
            itemtype = {field["n"]: field for field in itemtype["_fields_"]}[
                segment
            ]

        return itemtype

    @staticmethod
    def _set_itemtype_by_path(
        path: List[Union[int, str]],
        argtypes: List[Definition],
        restype: Optional[Definition],
        itemtype: Definition,
    ) -> Tuple[List[Definition], Optional[Definition]]:
        """
        Set zugbruecke argtype or restype by path

        Args:
            - path: List of int and/or str describing (part of) an argument or return value
            - argtypes: zugbruecke argument types
            - restype: zugbruecke return type
        Returns:
            Altered argtypes and return type definitions
        """

        # Remove pointer and array flags from path. TODO Function does not handle arrays.
        short_path = [
            segment
            for idx, segment in enumerate(path)
            if idx == 0 or isinstance(segment, str)
        ]

        if isinstance(short_path[0], int):  # function argument
            if len(short_path) == 1:
                argtypes[short_path[0]] = itemtype
                return argtypes, restype
            else:
                subtype = argtypes[short_path[0]]
        elif short_path[0] == "r":  # function return value
            if len(short_path) == 1:
                return argtypes, itemtype
            else:
                subtype = restype
        else:
            raise DataMemsyncpathError(
                f'short_path[0] is neither return value ("r") nor parameter (type int) "{short_path[0]}"'
            )

        # Step through short path to argument type ...
        for segment in short_path[1:-1]:
            # Go deeper ...
            subtype = subtype.get_field(name = segment)

        subtype.set_field(name = short_path[-1], definition = itemtype)

        return argtypes, restype

    def _unpack_memory(
        self, mempkg: Mempkg, args: List[Any], retval: Optional[Any] = None,
    ):
        """
        Data is unpacked. Potentially allocated on remote side.
        Server & client.

        Args:
            - mempkg: Memory package
            - args: Raw arguments
            - retval: Raw return value
        Returns:
            Nothing
        """

        # Generate pointer to passed data
        ptr = mempkg.make_pointer()

        # Search for pointer in passed arguments
        item = self._get_item_by_path(
            self._pointer[:-1], args, retval
        )

        # Is this an already existing pointer, which has to be given a new value?
        if hasattr(item, "contents"):
            # Is the pointer pointing to another pointer?
            if hasattr(item.contents, "value"):
                # Is the pointer empty?
                if item.contents.value is None:
                    # Overwrite the pointer's value
                    item.contents.value = ptr.value
                    # Get out of here HACK
                    return

        # If we're in the top level arguments or an array ...
        if isinstance(self._pointer[-1], int):
            # Handle deepest instance (exchange element in list/tuple) HACK
            item[self._pointer[-1]] = ptr
        # If we're at a field of a struct
        else:
            # There is a chance that the pointer has been stripped away ...
            item = strip_pointer(item)
            # A c_void_p NULL pointer in a struct is represented by None and must be substituted
            if getattr(item, self._pointer[-1]) is None:
                setattr(item, self._pointer[-1], ptr)
            # Anything else must be overwritten with the right type (likely on client side)
            else:
                setattr(
                    item,
                    self._pointer[-1],
                    ctypes.cast(
                        ptr,
                        ctypes.POINTER(getattr(item, self._pointer[-1])._type_),
                    ),
                )

        # Store the server's memory address
        mempkg.local_addr = ptr.value

    def _unpack_null(self, args: List[Any]):
        """
        Null-pointer unpacking prior to func call. No data is unpacked.
        Server only.

        Args:
            - args: Raw arguments
        Returns:
            Nothing
        """

        # If this is a return value, do nothing at this stage
        if self._pointer[0] == "r":
            return

        # If this is a pointer to a pointer
        if self._pointer[-1] == FLAG_POINTER:  # likely for R-strings only
            ptr = ctypes.pointer(ctypes.c_void_p())
            shift = 1  # cut off 1 element from path
        else:
            ptr = ctypes.c_void_p()
            shift = 0

        # Search for pointer in passed arguments
        arg = self._get_item_by_path(
            self._pointer[: (-1 - shift)], args
        )

        # If we're in the top level arguments or an array ...
        if isinstance(self._pointer[-1 - shift], int):
            # Handle deepest instance (exchange element in list/tuple) HACK
            arg[self._pointer[-1 - shift]] = ptr
        # If we're at a field of a struct
        else:
            # Handle deepest instance
            setattr(arg.contents, self._pointer[-1 - shift], ptr)

    def apply_one(
        self,
        cache: CacheABC,
        argtypes: List[Definition],
        restype: Optional[Definition] = None,
    ) -> Tuple[List[Definition], Optional[Definition]]:
        """
        Apply memsync definition to zugbruecke argtypes and restype definitions.
        Types are switched to void pointers.

        Args:
            - cache: cached types
            - argtypes: zugbruecke argument type definitions
            - restype: zugbruecke return type definition
        Returns:
            Altered argtypes and return type definitions
        """

        argtypes, restype = self._set_itemtype_by_path(
            path = self._pointer,
            argtypes = argtypes,
            restype = restype,
            itemtype = Definition.from_data_type(
                cache = cache,
                data_type = ctypes.c_void_p,  # HACK make memory sync pointers type agnostic
            ),  # New definition to replace the old one with
        )

        return argtypes, restype

    def pkg_memory(self, args: List[Any], retval: Optional[Any] = None) -> Mempkg:
        """
        Client. Pkg memory prior to call.

        Args:
            args: Raw function arguments
            memsyncs: Memsync definitions
        Returns:
            Memory package
        """

        # Search for pointer
        ptr = self._get_item_by_path(self._pointer, args, retval)

        # Convert argument of custom type into ctypes datatype TODO more checks needed!
        if self._custom is not None:
            ptr = self._custom.from_param(ptr)
            if not hasattr(ptr, 'contents'):
                ptr = ctypes.pointer(ptr)

        # Unicode char size if relevant
        wchar = ctypes.sizeof(ctypes.c_wchar) if self._unic else None

        # Check for NULL pointer
        if ptr is None or is_null_pointer(ptr):
            return Mempkg(
                data = b'',
                local_addr = None,
                remote_addr = None,
                wchar = wchar,
            )

        if self._null:
            # Get length of null-terminated string
            length = self._get_str_len(ptr, bool(wchar))
        else:
            # Compute actual length
            length = (
                self._get_arb_len(args, retval)
                * self._size
            )

        return Mempkg.from_pointer(ptr = ptr, length = length, wchar = wchar)

    def update_memory(self, mempkg: Mempkg, args: List[Any], retval: Optional[Any] = None):
        """
        Server. Used instead of pkg before return shipment to client.

        Args:
            - mempkg: Memory package
        Returns:
            Nothing
        """

        # If memory for pointer was allocated here on server side
        if mempkg.local_addr is None:
            # Update memory package completely
            mempkg.update(self.pkg_memory(args, retval))

        # If pointer pointed to data on client side
        else:
            # Overwrite old data in package with new data from memory
            mempkg.update_data()

    def unpkg_memory(self, mempkg: Mempkg, args: List[Any], retval: Optional[Any] = None, is_server: bool = False,):
        """
        Client/Server.

        Args:
            mempkg: Memory package from shipping
            args: Raw function arguments
            retval: Raw function return value
        Returns:
            Nothing
        """

        if is_server:

            # Is this a null pointer?
            if mempkg.remote_addr is None:
                # Insert new NULL pointer
                self._unpack_null(args)

            else:
                # Unpack one memory section / item
                self._unpack_memory(mempkg, args)

        else:

            # If memory for pointer has been allocated by remote side
            if mempkg.local_addr is None:
                # Unpack one memory section / item
                self._unpack_memory(mempkg, args, retval)

            # If pointer pointed to data
            else:
                # Overwrite pointer
                mempkg.overwrite()

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

        # In older versions of zugbruecke type could only be string - struct names in cache changed though
        if 'type' in definition.keys() and not isinstance(definition['type'], str):
            if type(definition['type']).__name__ == SIMPLE_GROUP:
                definition['type'] = definition['type'].__name__
            elif type(definition['type']).__name__ == STRUCT_GROUP:
                definition['type'] = DefinitionStruct.from_data_type(cache = cache, data_type = definition['type']).type_name
            else:
                raise TypeError('unhandled type in memsync definition')

        return cls(**definition, cache = cache)

    @classmethod
    def from_raws(cls, definitions: List[Dict], cache: CacheABC) -> List[DefinitionMemsyncABC]:
        """
        Ingest raw definitions given by user
        """

        return [cls.from_raw(definition, cache = cache) for definition in definitions]

    @staticmethod
    def apply_many(
        cache: CacheABC,
        memsyncs: List[DefinitionMemsyncABC],
        argtypes: List[Definition],
        restype: Optional[Definition] = None,
    ) -> Tuple[List[Definition], Optional[Definition]]:
        """
        Apply memsync definitions to zugbruecke argtypes and restype definitions.

        Args:
            - cache: cached types
            - memsyncs: List of memsync definitions
            - argtypes: zugbruecke argument type definitions
            - restype: zugbruecke return type definition
        Returns:
            Nothing
        """

        for memsync in memsyncs:
            argtypes, restype = memsync.apply_one(
                cache = cache,
                argtypes = argtypes,
                restype = restype,
            )

        return argtypes, restype

    @staticmethod
    def pkg_memories(
        args: List[Any],
        memsyncs: List[DefinitionMemsyncABC],
    ) -> List[Mempkg]:
        """
        Client. Before initial shipment.

        Args:
            args: Raw function arguments
            memsyncs: Memsync definitions
        Returns:
            List of memory packages for shipping
        """

        return [memsync.pkg_memory(args) for memsync in memsyncs]

    @staticmethod
    def update_memories(
        args: List[Any],
        retval: Any,
        mempkgs: List[Mempkg],
        memsyncs: List[DefinitionMemsyncABC],
    ):
        """
        Server. After call, for return shipment.

        Args:
            args: Raw function arguments
            retval: Raw function return value
            mempkgs: List of packed memory packages from shipping
            memsyncs: Memsync definitions
        Returns:
            Nothing
        """

        # Iterate over memory package dicts
        for mempkg, memsync in zip(mempkgs, memsyncs):
            memsync.update_memory(mempkg, args, retval)

    @staticmethod
    def unpkg_memories(
        args: List[Any],
        retval: Optional[Any],
        mempkgs: List[Mempkg],
        memsyncs: List[DefinitionMemsyncABC],
        is_server: bool = False,
    ):
        """
        Client/Server. After shipment.

        Args:
            args: Raw function arguments
            retval: Raw function return value
            mempkgs: List of memory packages from shipping
            memsyncs: Memsync definitions
        Returns:
            Nothing
        """

        for mempkg, memsync in zip(mempkgs, memsyncs):
            memsync.unpkg_memory(mempkg, args, retval, is_server)
