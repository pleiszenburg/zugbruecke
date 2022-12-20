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

from ..const import GROUP_VOID
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
            self.__pack_memory_item__(memsync, args)
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
                self.__unpack_memory_item_overwrite__(mempkg, memsync, args)

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
                    self.__pack_memory_item__(memsync, args, retval)
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
                self.__unpack_memory_item_null__(mempkg, memsync, args)

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

    def __pack_memory_item__(self, memsync_d, args_tuple, return_value=None):

        # Search for pointer
        pointer = self._get_item_by_path(
            memsync_d["p"], args_tuple, return_value
        )

        # Convert argument into ctypes datatype TODO more checks needed!
        if "_c" in memsync_d.keys():
            pointer = ctypes.pointer(memsync_d["_c"].from_param(pointer))

        # Unicode char size if relevant
        w = WCHAR_BYTES if memsync_d["w"] else None

        # Check for NULL pointer
        if pointer is None or is_null_pointer(pointer):
            return {"d": b"", "l": 0, "a": None, "_a": None, "w": w}

        if memsync_d["n"]:
            # Get length of null-terminated string
            length = self._get_str_len(pointer, bool(w))
        else:
            # Compute actual length
            length = (
                self._get_arb_len(memsync_d, args_tuple, return_value)
                * memsync_d["s"]
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

    def __swap_memory_addresses__(self, memory_d):

        memory_d.update({"a": memory_d.get("_a", None), "_a": memory_d.get("a", None)})

    def __unpack_memory_item_data__(
        self, memory_d, memsync_d, args_tuple, return_value=None
    ):

        # Swap local and remote memory addresses
        self.__swap_memory_addresses__(memory_d)

        # Search for pointer in passed arguments
        pointer_arg = self._get_item_by_path(
            memsync_d["p"][:-1], args_tuple, return_value
        )

        # Adjust Unicode wchar length
        if memsync_d["w"]:
            self._adjust_wchar_length(memory_d)

        # Generate pointer to passed data
        pointer = generate_pointer_from_bytes(memory_d["d"])

        # Is this an already existing pointer, which has to be given a new value?
        if hasattr(pointer_arg, "contents"):
            # Is the pointer pointing to another pointer?
            if hasattr(pointer_arg.contents, "value"):
                # Is the pointer empty?
                if pointer_arg.contents.value is None:
                    # Overwrite the pointer's value
                    pointer_arg.contents.value = pointer.value
                    # Get out of here HACK
                    return

        # If we're in the top level arguments or an array ...
        if isinstance(memsync_d["p"][-1], int):
            # Handle deepest instance (exchange element in list/tuple) HACK
            pointer_arg[memsync_d["p"][-1]] = pointer
        # If we're at a field of a struct
        else:
            # There is a chance that the pointer has been stripped away ...
            if hasattr(pointer_arg, "contents"):
                pointer_arg = pointer_arg.contents
            # A c_void_p NULL pointer in a struct is represented by None and must be substituted
            if getattr(pointer_arg, memsync_d["p"][-1]) is None:
                setattr(pointer_arg, memsync_d["p"][-1], pointer)
            # Anything else must be overwritten with the right type (likely on client side)
            else:
                setattr(
                    pointer_arg,
                    memsync_d["p"][-1],
                    ctypes.cast(
                        pointer,
                        ctypes.POINTER(getattr(pointer_arg, memsync_d["p"][-1])._type_),
                    ),
                )

        # Store the server's memory address
        memory_d["a"] = pointer.value

    def __unpack_memory_item_null__(self, memory_d, memsync_d, args_tuple):

        # Swap local and remote memory addresses
        self.__swap_memory_addresses__(memory_d)

        # If this is a return value, do nothing at this stage
        if memsync_d["p"][0] == "r":
            return

        # If this is a pointer to a pointer
        if memsync_d["p"][-1] == -1:
            pointer = ctypes.pointer(ctypes.c_void_p())
            path_shift = 1  # cut off 1 element from path
        else:
            pointer = ctypes.c_void_p()
            path_shift = 0

        # Search for pointer in passed arguments
        pointer_arg = self._get_item_by_path(
            memsync_d["p"][: (-1 - path_shift)], args_tuple
        )

        # If we're in the top level arguments or an array ...
        if isinstance(memsync_d["p"][-1 - path_shift], int):
            # Handle deepest instance (exchange element in list/tuple) HACK
            pointer_arg[memsync_d["p"][-1 - path_shift]] = pointer
        # If we're at a field of a struct
        else:
            # Handle deepest instance
            setattr(pointer_arg.contents, memsync_d["p"][-1 - path_shift], pointer)

    def __unpack_memory_item_overwrite__(self, memory_d, memsync_d, args_tuple):

        # Swap local and remote memory addresses
        self.__swap_memory_addresses__(memory_d)

        # Adjust Unicode wchar length
        if memsync_d["w"]:
            self._adjust_wchar_length(memory_d)

        # Overwrite the local pointers with new data
        overwrite_pointer_with_bytes(ctypes.c_void_p(memory_d["a"]), memory_d["d"])
