# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/arg_contents.py: (Un-) packing of argument contents

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
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..const import (
    FLAG_POINTER,
    GROUP_VOID,
    GROUP_FUNDAMENTAL,
    GROUP_STRUCT,
    GROUP_FUNCTION,
)
from ..callback_client import CallbackClient
from ..callback_server import CallbackServer
from ..errors import DataFlagError, DataGroupError
from .memory import is_null_pointer


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class ArgContents:
    """
    MIXIN: Argument contents (without memory sync)
    """

    def pack_args(self, args: Tuple[Any], argtypes: List[Dict], conv: Optional[str] = None) -> List[Any]:
        """
        Args:
            - args: raw arguments
            - argtypes: zugbruecke argtype definitions
            - conv: optional name of calling convention
        Returns:
            Packed list of arguments for shipping
        """

        # Everything is normal
        if len(args) == len(argtypes):
            return [
                self._pack_item(arg, argtype)
                for arg, argtype in zip(args, argtypes)
            ]

        # Function has likely not been configured but there are arguments
        if len(args) > 0 and len(argtypes) == 0:
            return list(args)  # let's try ... TODO catch pickling errors

        if (
            len(args) > len(argtypes)
            and len(argtypes) > 0
            and conv == "cdll"
        ):
            return [
                self._pack_item(arg, argtype)
                for arg, argtype in zip(args[:len(argtypes)], argtypes)
            ] + list(args[len(argtypes):])  # let's try ... TODO catch pickling errors

        # Number of arguments is just wrong
        raise TypeError  # Must be TypeError for ctypes compatibility

    def unpack_args(self, args: List[Any], argtypes: List[Dict], conv: Optional[str] = None) -> List[Any]:
        """
        Args:
            - args: packed list of arguments from shipping
            - argtypes: zugbruecke argtype definitions
            - conv: optional name of calling convention
        Returns:
            Raw arguments
        """

        # Everything is normal
        if len(args) == len(argtypes):
            return [
                self._unpack_item(arg, argtype)
                for arg, argtype in zip(args, argtypes)
            ]

        # Function has likely not been configured but there are arguments
        if len(args) > 0 and len(argtypes) == 0:
            return args

        if (
            len(args) > len(argtypes)
            and len(argtypes) > 0
            and conv == "cdll"
        ):
            return [
                self._unpack_item(arg, argtype)
                for arg, argtype in zip(args[:len(argtypes)], argtypes)
            ] + args[len(argtypes):]

        # Number of arguments is just wrong
        raise TypeError  # Highly unlikely case, pack_args will fail instead

    def pack_retval(self, value: Any, restype: Dict) -> Any:  # return_msg_pack
        """
        Args:
            - value: raw return value
            - restype: zugbruecke restype definition
        Returns:
            Packed return value for shipping
        """

        if value is None:
            return None

        return self._pack_item(value, restype)

    def unpack_retval(self, value: Any, restype: Dict) -> Any:  # return_msg_unpack
        """
        Args:
            - value: packed return value from shipping
            - restype: zugbruecke restype definitions
        Returns:
            Raw return value
        """

        if value is None:
            return None

        # If this is not a fundamental datatype or if there is a pointer involved, just unpack
        if (
            not restype["g"] == GROUP_FUNDAMENTAL
            or FLAG_POINTER in restype["f"]
        ):
            return self._unpack_item(value, restype)

        # The original ctypes strips away ctypes datatypes for fundamental
        # (non-pointer, non-struct) return values and returns plain Python
        # data types instead - the unpacked result requires stripping
        return self._strip_simplecdata(
            self._unpack_item(value, restype)
        )

    def sync_args(self, old_args: List[Any], new_args: List[Any], argtypes: List[Dict]):
        """
        Args:
            - old_args: Raw arguments
            - new_args: Raw arguments
        Returns:
            Nothing
        """

        # Step through arguments
        for old_arg, new_arg, argtype in zip(
            old_args, new_args, argtypes
        ):
            self._sync_arg(old_arg, new_arg, argtype)

    @staticmethod
    def _strip_pointer(item: Any) -> Any:  # _strip_pointer
        """
        Args:
            - item: ctypes pointer object
        Returns:
            ctypes object, extracted from pointer
        """

        # Handle pointer object
        if hasattr(item, "contents"):
            return item.contents

        # Handle reference (byref) 'light pointer'
        if hasattr(item, "_obj"):
            return item._obj

        # Object was likely not provided as a pointer
        return item

    @staticmethod
    def _strip_simplecdata(item: Any) -> Any:
        """
        Args:
            - item: potentially some ctypes SimpleCData object
        Returns:
            Raw value, extracted from ctypes SimpleCData object
        """

        return getattr(item, "value", item)

    def _pack_item(self, item: Any, itemtype: Dict) -> Any:
        """
        Args:
            - item: raw argument / return value
            - itemtype: zugbruecke argtype / restype definition
        Returns:
            Packed argument / return value for shipping
        """

        # The non-trivial case first, non-scalars: arrays
        if not itemtype["s"]:
            # Unpack every item in array
            return self._pack_array(item, itemtype)

        # Strip away the pointers ... (all flags are pointers in this case)
        for flag in itemtype["f"]:
            if flag != FLAG_POINTER:
                raise DataFlagError(f'unknown non-pointer flag for scalar "{flag:d}"')
            if is_null_pointer(item):
                return None  # Just return None - will (hopefully) be overwritten by memsync
            item = self._strip_pointer(item)

        # Handle fundamental types
        if itemtype["g"] == GROUP_FUNDAMENTAL:
            # Append argument to list ...
            return self._strip_simplecdata(item)

        # Handle structs
        if itemtype["g"] == GROUP_STRUCT:
            # Reclusively call this routine for packing structs
            return self._pack_struct(item, itemtype)

        # Handle functions
        if itemtype["g"] == GROUP_FUNCTION:
            # Packs functions and registers them at RPC server
            return self._pack_func(item, itemtype)

        # Handle everything else ...
        return None  # Just return None - will (hopefully) be overwritten by memsync

    def _pack_array(self, array: Any, arraytype: Dict, start: int = 0) -> Any:
        """
        Recursive function, packing one dimension per call

        Args:
            - array: raw argument / return array, n-dimensional
            - arraytype: zugbruecke argtype / restype definition
            - start: dimension to start with when packing
        Returns:
            Packed argument / return array for shipping
        """

        for idx, flag in enumerate(arraytype["f"][start:], start = start):

            # Is pointer?
            if flag == FLAG_POINTER:
                # Strip pointer
                array = self._strip_pointer(array)

            # Is array dimension?
            elif flag > 0:
                # Only dive deeper if this is not the last flag
                if idx < len(arraytype["f"]) - 1:
                    array = [
                        self._pack_array(
                            dim, arraytype, start=idx + 1
                        )
                        for dim in array[:]
                    ]
                else:
                    array = array[:]
                    if arraytype["g"] == GROUP_STRUCT:
                        array = [
                            self._pack_struct(struct, arraytype) for struct in array
                        ]

            # Handle unknown flags
            else:
                raise DataFlagError("unknown non-pointer flag for array")

        return array

    def _pack_func(self, func: Callable, functype: Dict) -> str:
        """
        Args:
            - func: callable
            - functype: zugbruecke argtype / restype definition
        Returns:
            (Generated) name of func for shipping
        """

        # HACK if on server, just return None
        if self._is_server:
            return None

        # Use memory address of function pointer as unique name/ID
        name = f"func_{id(func):x}"

        # Has callback translator not been built yet?
        if name not in self._cache.handle.keys():
            # Generate and store callback in cache
            self._cache.handle[name] = CallbackClient(
                name = name,
                handler = func,
                rpc_server = self._callback_server,
                data = self,
                log = self._log,
                argtypes_d = functype["_argtypes_"],
                restype_d = functype["_restype_"],
                memsync_d = self.unpack_definition_memsync(functype["_memsync_"]),
            )

        # Return name of callback entry
        return name

    def _pack_struct(self, struct: Any, structtype: Dict) -> List[Tuple[str, Any]]:
        """
        Args:
            - struct: raw argument / return struct
            - structtype: zugbruecke argtype / restype definition
        Returns:
            Packed list of argument / return field names and values of struct as tuples for shipping
        """

        # Return parameter message list - MUST WORK WITH PICKLE
        return [
            (
                fieldtype["n"],
                self._pack_item(
                    getattr(struct, fieldtype["n"]), fieldtype
                ),
            )
            for fieldtype in structtype["_fields_"]
        ]

    def _sync_arg(self, old_arg: Any, new_arg: Any, argtype: Dict):
        """
        Args:
            - old_arg: Raw argument
            - new_arg: Raw argument
            - argtype: zugbruecke argtype definition
        Returns:
            Nothing
        """

        # The non-trivial case first, arrays
        if not argtype["s"]:
            # Sync items in array
            self._sync_array(old_arg, new_arg, argtype)
            # Leave
            return

        # Do not do this for void pointers, likely handled by memsync
        if argtype["g"] == GROUP_VOID:
            return

        # Strip away the pointers ... (all flags are pointers in this case)
        for flag in argtype["f"]:
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            old_arg = self._strip_pointer(old_arg)
            new_arg = self._strip_pointer(new_arg)

        if argtype["g"] == GROUP_FUNDAMENTAL:
            if hasattr(old_arg, "value"):
                old_arg.value = new_arg.value
            else:
                pass  # only relevant within structs or for actual pointers to scalars
            return

        if argtype["g"] == GROUP_STRUCT:
            self._sync_struct(old_arg, new_arg, argtype)
            return

        if argtype["g"] == GROUP_FUNCTION:
            return  # Nothing to do?

        raise DataGroupError("unexpected datatype group")

    def _sync_array(self, old_array: Any, new_array: Any, arraytype: Dict, start: int = 0):
        """
        Recursive function, syncing one dimension per call

        Args:
            - old_array: Raw argument
            - new_array: Raw argument
            - arraytype: zugbruecke argtype definition
            - start: dimension to start with when syncing
        Returns:
            Nothing
        """

        for idx, flag in enumerate(arraytype["f"][start:], start = start):

            # Handle pointers
            if flag == FLAG_POINTER:
                old_array = self._strip_pointer(old_array)
                new_array = self._strip_pointer(new_array)

            # Handle arrays
            elif flag > 0:
                # Only dive deeper if this is not the last flag
                if idx < len(arraytype["f"]) - 1:
                    for old_dim, new_dim in zip(old_array[:], new_array[:]):
                        self._sync_array(
                            old_dim,
                            new_dim,
                            arraytype,
                            start=idx + 1,
                        )
                else:
                    if arraytype["g"] == GROUP_FUNDAMENTAL:
                        old_array[:] = new_array[:]
                    elif arraytype["g"] == GROUP_STRUCT:
                        for old_struct, new_struct in zip(old_array[:], new_array[:]):
                            self._sync_struct(
                                old_struct, new_struct, arraytype
                            )
                    elif arraytype["g"] == GROUP_FUNCTION:
                        raise NotImplementedError(
                            "functions in arrays are not supported"
                        )
                    else:
                        raise DataGroupError("unexpected datatype group")

            # Handle unknown flags
            else:
                raise DataFlagError("unknown non-pointer flag for array")

    def _sync_struct(self, old_struct: Any, new_struct: Any, structtype: Dict):
        """
        Args:
            - old_struct: raw argument struct
            - new_struct: raw argument struct
            - structtype: zugbruecke argtype definition
        Returns:
            Nothing
        """

        # Step through arguments
        for fieldtype in structtype["_fields_"]:

            self._sync_arg(
                getattr(old_struct, fieldtype["n"]),
                getattr(new_struct, fieldtype["n"]),
                fieldtype,
            )

    def _unpack_item(self, item: Any, itemtype: Dict) -> Any:
        """
        Args:
            - item: packaged argument / return value from shipping
            - itemtype: zugbruecke argtype / restype definition
        Returns:
            Raw argument / return value
        """

        # The non-trivial case first, arrays
        if not itemtype["s"]:
            # Unpack items in array
            _, item = self._unpack_array(item, itemtype)
            return item

        # Handle fundamental types
        if itemtype["g"] == GROUP_FUNDAMENTAL:
            item = getattr(ctypes, itemtype["t"])(item)
        # Handle structs
        elif itemtype["g"] == GROUP_STRUCT:
            item = self.__unpack_item_struct__(item, itemtype)
        # Handle functions
        elif itemtype["g"] == GROUP_FUNCTION:
            item = self.__unpack_item_function__(item, itemtype)
        # Handle voids (likely mensync stuff)
        elif itemtype["g"] == GROUP_VOID:
            # Return a placeholder
            return None
        # Handle everything else ...
        else:
            raise DataGroupError("unexpected datatype group")

        # Step through flags in reverse order (if it's not a memsync field)
        for flag in reversed(itemtype["f"]):
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            item = ctypes.pointer(item)

        return item

    def _unpack_array(self, array: Any, arraytype: Dict, start: int = 0) -> Tuple[Any, Any]:
        """
        Recursive function, packing one dimension per call

        Args:
            - array: packed argument / return array, n-dimensional, from shipping
            - arraytype: zugbruecke argtype / restype definition
            - start: flag to start with when packing
        Returns:
            Tuple of ctypes type and unpacked argument / return array
        """

        # Extract the flag
        flag = arraytype["f"][start]

        # Dive deeper?
        if start < len(arraytype["f"]) - 1:

            # Get index of next flag
            next_start = start + 1

            # If it's a Python list, dive once per element of list
            if isinstance(array, list) and flag != FLAG_POINTER:

                dims = [
                    self._unpack_array(
                        dim, arraytype, start=next_start
                    )
                    for dim in array
                ]
                subtype = dims[0][0]
                array = [dim[1] for dim in dims]

            # Likely a scalar or a ctypes object
            else:

                subtype, array = self._unpack_array(
                    array, arraytype, start=next_start
                )

            # Handle pointers
            if flag == FLAG_POINTER:
                subtype = ctypes.POINTER(subtype)
                array = ctypes.pointer(array)
            # Handle arrays
            elif flag > 0:
                subtype = subtype * flag
                array = subtype(*array)
            # Handle unknown flags
            else:
                raise DataFlagError(f'unknown non-pointer flag for array "{flag:d}"')

        # No dive, we're at the bottom - just get the original ctypes type
        else:

            if flag == FLAG_POINTER:
                raise DataFlagError("unexpected pointer flag for array")

            if arraytype["g"] == GROUP_FUNDAMENTAL:
                subtype = getattr(ctypes, arraytype["t"]) * flag
                array = subtype(*array)
            elif arraytype["g"] == GROUP_STRUCT:
                subtype = self._cache.struct[arraytype["t"]] * flag
                array = subtype(
                    *(self.__unpack_item_struct__(dim, arraytype) for dim in array)
                )
            elif arraytype["g"] == GROUP_FUNCTION:
                raise NotImplementedError("functions in arrays are not supported")
            else:
                raise DataGroupError("unexpected datatype group")

        return subtype, array

    def __unpack_item_function__(self, func_name, func_def_dict):

        # HACK if this function is called on the client, just return None
        if not self._is_server:
            return None

        # Has callback translator been built?
        if func_name in self._cache.handle.keys():

            # Just return handle
            return self._cache.handle[func_name]

        # Generate, decorate and store callback translator in cache
        self._cache.handle[func_name] = func_def_dict["_factory_type_"](
            CallbackServer(
                name = func_name,
                rpc_client = self._callback_client,
                data = self,
                log = self._log,
                argtypes_d = func_def_dict["_argtypes_"],
                restype_d = func_def_dict["_restype_"],
                memsync_d = self.unpack_definition_memsync(func_def_dict["_memsync_"]),
            )
        )

        # Return name of callback entry
        return self._cache.handle[func_name]

    def __unpack_item_struct__(self, args_list, struct_def_dict):

        # Generate new instance of struct datatype
        struct_inst = self._cache.struct[struct_def_dict["t"]]()

        # Step through arguments
        for field_def_dict, field_arg in zip(struct_def_dict["_fields_"], args_list):

            # HACK is field_arg[1] is None, it's likely a function pointer sent back from Wine side - skip
            if field_arg[1] is None:
                continue

            field_value = self._unpack_item(field_arg[1], field_def_dict)

            try:

                setattr(
                    struct_inst,  # struct instance to be modified
                    field_arg[0],  # field name (from tuple)
                    field_value,  # field value
                )

            except TypeError:  # TODO HACK relevant for structs & callbacks & memsync together

                setattr(
                    struct_inst,  # struct instance to be modified
                    field_arg[0],  # field name (from tuple)
                    ctypes.cast(field_value, ctypes.c_void_p),
                )

        return struct_inst
