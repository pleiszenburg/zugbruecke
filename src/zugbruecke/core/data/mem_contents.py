# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/data/mem_contents.py: (Un-) packing of memory

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

from ..const import FLAG_POINTER, GROUP_VOID
from ..errors import DataMemsyncpathError
from ..typeguard import typechecked

from .memory import (
    generate_pointer_from_bytes,
    is_null_pointer,
    overwrite_pointer_with_bytes,
    serialize_pointer_into_bytes,
    strip_pointer,
    strip_simplecdata,
)

WCHAR_BYTES = ctypes.sizeof(ctypes.c_wchar)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Memory content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class MemContents:
    """
    MIXIN: Memory contents (memory sync)
    """

    def apply_memsync(
        self, memsyncs: List[Dict], argtypes: List[Dict], restype: Dict,
    ):
        """
        Apply memsync definitions to zugbruecke argtypes and restype definitions.
        Types are switched to void pointers.

        Args:
            - memsyncs: List of memsync definitions
            - argtypes: zugbruecke argument type definitions
            - restype: zugbruecke return type definition
        Returns:
            Nothing
        """

        # Iterate over memory segments which must be kept in sync
        for memsync in memsyncs:

            # Get type of pointer argument
            itemtype = self._get_itemtype_by_path(
                memsync["p"], argtypes, restype,
            )

            # HACK make memory sync pointers type agnostic
            itemtype["g"] = GROUP_VOID
            itemtype["t"] = None  # no type string

    def pack_memory_on_client(self, args: List[Any], memsyncs: List[Dict],) -> List[Dict]:
        """
        Args:
            args: Raw function arguments
            memsyncs: Memsync definitions
        Returns:
            List of memory packages for shipping
        """

        # Pack data for every pointer into package
        return [
            self._pack_memory(memsync, args)
            for memsync in memsyncs
        ]

    def unpack_memory_on_client(
        self, args: List[Any], retval: Any, mempkgs: List[Dict], memsyncs: List[Dict],
    ):
        """
        Args:
            args: Raw function arguments
            retval: Raw function return value
            mempkgs: List of memory packages from shipping
            memsyncs: Memsync definitions
        Returns:
            Nothing
        """

        # Iterate over memory package dicts
        for mempkg, memsync in zip(mempkgs, memsyncs):

            # If memory for pointer has been allocated by remote side
            if mempkg["_a"] is None:
                # Unpack one memory section / item
                self.__unpack_memory_item_data__(
                    mempkg, memsync, args, retval
                )

            # If pointer pointed to data
            else:
                # Overwrite pointer
                self._unpack_memory_overwrite(mempkg, memsync)

    def pack_memory_on_server(
        self, args: List[Any], retval: Any, mempkgs: List[Dict], memsyncs: List[Dict],
    ):
        """
        Args:
            args: Raw function arguments
            retval: Raw function return value
            mempkgs: List of memory packages from shipping
            memsyncs: Memsync definitions
        Returns:
            Nothing
        """

        # Iterate through pointers and serialize them
        for mempkg, memsync in zip(mempkgs, memsyncs):

            # If memory for pointer was allocated here on server side
            if mempkg["a"] is None:
                mempkg.update(
                    self._pack_memory(memsync, args, retval)
                )

            # If pointer pointed to data on client side
            else:
                # Overwrite old data in package with new data from memory
                mempkg["d"] = serialize_pointer_into_bytes(
                    ctypes.c_void_p(mempkg["a"]), mempkg["l"]
                )

    def unpack_memory_on_server(self, args: List[Any], mempkgs: List[Dict], memsyncs: List[Dict],):
        """
        Args:
            args: Raw function arguments
            mempkgs: List of memory packages from shipping
            memsyncs: Memsync definitions
        Returns:
            Nothing
        """

        # Iterate over memory segments, which must be kept in sync
        for mempkg, memsync in zip(mempkgs, memsyncs):

            # Is this a null pointer?
            if mempkg["a"] is None:
                # Insert new NULL pointer
                self._unpack_memory_null(mempkg, memsync, args)

            else:
                # Unpack one memory section / item
                self.__unpack_memory_item_data__(mempkg, memsync, args)

    def _adjust_wchar_length(self, mempkg: Dict):
        """
        Adjust number of bytes per unicode character

        Args:
            - mempkg: Memory package for/from shipping
        Returns:
            Nothing
        """

        old_len = mempkg["w"]
        new_len = WCHAR_BYTES

        if old_len == new_len:
            return

        tmp = bytearray(mempkg["l"] * new_len // old_len)

        for index in range(old_len if new_len > old_len else new_len):
            tmp[index::new_len] = mempkg["d"][index::old_len]

        mempkg["d"] = bytes(tmp)
        mempkg["l"] = len(mempkg["d"])
        mempkg["w"] = WCHAR_BYTES

    def _get_item_by_path(
        self, path: List[Union[int, str]], args: List[Any], retval: Optional[Any] = None,
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

                self._log.err(segment)
                raise NotImplementedError("array elements can yet not be addressed")

        return element

    def _get_itemtype_by_path(
        self, path: List[Union[int, str]], argtypes: List[Dict], restype: Dict,
    ) -> Dict:
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

    def _get_str_len(self, ptr: Any, is_unicode: bool) -> int:
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

    def _get_arb_len(self, memsync: Dict, args: List[Any], retval: Optional[Any] = None) -> int:
        """
        Get length of arbitrary data

        Args:
            - memsync: Memsync definition
            - args: Raw arguments
            - retval: Raw return value
        Returns:
            Length in bytes
        """

        # There is no function defining the length?
        if "_f" not in memsync.keys():

            # Search for length
            length = self._get_item_by_path(
                memsync["l"], args, retval
            )

            # Length might come from ctypes or a Python datatype
            return strip_simplecdata(length)

        # Make sure length can be computed from a tuple of arguments
        assert isinstance(memsync["l"], tuple)

        # Compute length from arguments and return
        return memsync["_f"](
            *(
                self._get_item_by_path(path, args, retval)
                for path in memsync["l"]
            )
        )

    def _pack_memory(self, memsync: Dict, args: List[Any], retval: Optional[Any] = None) -> Dict:
        """
        Args:
            - memsync: Memsync definition
            - args: Raw arguments
            - retval: Raw return value
        Returns:
            Memory package
        """

        # Search for pointer
        pointer = self._get_item_by_path(
            memsync["p"], args, retval
        )

        # Convert argument of custom type into ctypes datatype TODO more checks needed!
        if "_c" in memsync.keys():
            pointer = ctypes.pointer(memsync["_c"].from_param(pointer))

        # Unicode char size if relevant
        w = WCHAR_BYTES if memsync["w"] else None

        # Check for NULL pointer
        if pointer is None or is_null_pointer(pointer):
            return {"d": b"", "l": 0, "a": None, "_a": None, "w": w}

        if memsync["n"]:
            # Get length of null-terminated string
            length = self._get_str_len(pointer, bool(w))
        else:
            # Compute actual length
            length = (
                self._get_arb_len(memsync, args, retval)
                * memsync["s"]
            )

        return {
            "d": serialize_pointer_into_bytes(
                pointer, length
            ),  # serialized data, '' if NULL pointer
            "l": length,  # length of serialized data
            "a": ctypes.cast(
                pointer, ctypes.c_void_p
            ).value,  # local pointer address as integer
            "_a": None,  # remote pointer has not been initialized
            "w": w,  # local length of Unicode wchar if required
        }

    def _swap_addr(self, mempkg: Dict):
        """
        Swaps local and remote memory addresses within memory package

        Args:
            - mempkg: Memory package from shipping
        Returns:
            Nothing
        """

        mempkg.update({"a": mempkg.get("_a", None), "_a": mempkg.get("a", None)})

    def __unpack_memory_item_data__(
        self, mempkg: Dict, memsync: Dict, args: List[Any], retval: Optional[Any] = None,
    ):
        """
        Data is unpacked. Potentially allocated on remote side.
        Server & client.

        Args:
            - mempkg: Memory package
            - memsync: Memsync definition
            - args: Raw arguments
            - retval: Raw return value
        Returns:
            Nothing
        """

        # Swap local and remote memory addresses
        self._swap_addr(mempkg)

        # Adjust Unicode wchar length
        if memsync["w"]:
            self._adjust_wchar_length(mempkg)

        # Generate pointer to passed data
        ptr = generate_pointer_from_bytes(mempkg["d"])

        # Search for pointer in passed arguments
        item = self._get_item_by_path(
            memsync["p"][:-1], args, retval
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
        if isinstance(memsync["p"][-1], int):
            # Handle deepest instance (exchange element in list/tuple) HACK
            item[memsync["p"][-1]] = ptr
        # If we're at a field of a struct
        else:
            # There is a chance that the pointer has been stripped away ...
            item = strip_pointer(item)
            # A c_void_p NULL pointer in a struct is represented by None and must be substituted
            if getattr(item, memsync["p"][-1]) is None:
                setattr(item, memsync["p"][-1], ptr)
            # Anything else must be overwritten with the right type (likely on client side)
            else:
                setattr(
                    item,
                    memsync["p"][-1],
                    ctypes.cast(
                        ptr,
                        ctypes.POINTER(getattr(item, memsync["p"][-1])._type_),
                    ),
                )

        # Store the server's memory address
        mempkg["a"] = ptr.value

    def _unpack_memory_null(self, mempkg: Dict, memsync: Dict, args: List[Any]):
        """
        Null-pointer unpacking on server-side prior to func call. No data is unpacked.
        Server only.

        Args:
            - mempkg: Memory package
            - memsync: Memsync definition
            - args: Raw arguments
        Returns:
            Nothing
        """

        # Swap local and remote memory addresses
        self._swap_addr(mempkg)

        # If this is a return value, do nothing at this stage
        if memsync["p"][0] == "r":
            return

        # If this is a pointer to a pointer
        if memsync["p"][-1] == FLAG_POINTER:  # likely for R-strings only
            ptr = ctypes.pointer(ctypes.c_void_p())
            shift = 1  # cut off 1 element from path
        else:
            ptr = ctypes.c_void_p()
            shift = 0

        # Search for pointer in passed arguments
        arg = self._get_item_by_path(
            memsync["p"][: (-1 - shift)], args
        )

        # If we're in the top level arguments or an array ...
        if isinstance(memsync["p"][-1 - shift], int):
            # Handle deepest instance (exchange element in list/tuple) HACK
            arg[memsync["p"][-1 - shift]] = ptr
        # If we're at a field of a struct
        else:
            # Handle deepest instance
            setattr(arg.contents, memsync["p"][-1 - shift], ptr)

    def _unpack_memory_overwrite(self, mempkg: Dict, memsync: Dict):
        """
        Existing memory overwrite.
        Client.

        Args:
            - mempkg: Memory package
            - memsync: Memsync definition
        Returns:
            Nothing
        """

        # Swap local and remote memory addresses
        self._swap_addr(mempkg)

        # Adjust Unicode wchar length
        if memsync["w"]:
            self._adjust_wchar_length(mempkg)

        # Overwrite the local pointers with new data
        overwrite_pointer_with_bytes(ctypes.c_void_p(mempkg["a"]), mempkg["d"])
