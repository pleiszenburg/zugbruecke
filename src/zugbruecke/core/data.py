# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data.py: (Un-) packing of arguments and return values

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
from typing import Any, Callable, List, Optional, Tuple

from .abc import CacheABC, DataABC, LogABC, RpcClientABC, RpcServerABC
from .cache import Cache
from .const import (
    FLAG_POINTER,
    SIMPLE_GROUP,
    STRUCT_GROUP,
    FUNC_GROUP,
)
from .callback_client import CallbackClient
from .callback_server import CallbackServer
from .definitions import Definition
from .errors import DataFlagError, DataGroupError
from .memory import is_null_pointer, strip_pointer, strip_simplecdata
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Data(DataABC):
    """
    Handles argument and return value contents, prepares stage for memsync if required
    """

    def __init__(
        self,
        log: LogABC,
        is_server: bool,
        callback_client: Optional[RpcClientABC] = None,
        callback_server: Optional[RpcServerABC] = None,
    ):

        self._log = log
        self._is_server = is_server

        self._callback_client = callback_client
        self._callback_server = callback_server

        self._cache = Cache()

    @property
    def cache(self) -> CacheABC:

        return self._cache

    def pack_args(self, args: List[Any], argtypes: List[Definition], conv: Optional[str] = None) -> List[Any]:
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

    def unpack_args(self, args: List[Any], argtypes: List[Definition], conv: Optional[str] = None) -> List[Any]:
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

    def pack_retval(self, value: Any, restype: Optional[Definition]) -> Any:
        """
        Args:
            - value: raw return value
            - restype: zugbruecke restype definition
        Returns:
            Packed return value for shipping
        """

        if value is None:
            return None

        if restype is None:
            return strip_simplecdata(value)

        return self._pack_item(value, restype)

    def unpack_retval(self, value: Any, restype: Optional[Definition]) -> Any:
        """
        Args:
            - value: packed return value from shipping
            - restype: zugbruecke restype definitions
        Returns:
            Raw return value
        """

        if value is None:
            return None

        if restype is None:
            return value

        # If this is not a fundamental datatype or if there is a pointer involved, just unpack
        if (
            not restype.GROUP == SIMPLE_GROUP
            or FLAG_POINTER in restype.flags
        ):
            return self._unpack_item(value, restype)

        # The original ctypes strips away ctypes datatypes for fundamental
        # (non-pointer, non-struct) return values and returns plain Python
        # data types instead - the unpacked result requires stripping
        return strip_simplecdata(
            self._unpack_item(value, restype)
        )

    def sync_args(self, old_args: List[Any], new_args: List[Any], argtypes: List[Definition]):
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

    def _pack_item(self, item: Any, itemtype: Definition) -> Any:
        """
        Args:
            - item: raw argument / return value
            - itemtype: zugbruecke argtype / restype definition
        Returns:
            Packed argument / return value for shipping
        """

        # The non-trivial case first, non-scalars: arrays
        if not itemtype.is_scalar:
            # Unpack every item in array
            return self._pack_array(item, itemtype)

        # Strip away the pointers ... (all flags are pointers in this case)
        for flag in itemtype.flags:
            if flag != FLAG_POINTER:
                raise DataFlagError(f'unknown non-pointer flag for scalar "{flag:d}"')
            if is_null_pointer(item):
                return None  # Just return None - will (hopefully) be overwritten by memsync
            item = strip_pointer(item)

        # Likely handled by memsync
        if itemtype.is_void:
            # Leave empty
            return None

        # Handle fundamental types
        if itemtype.GROUP == SIMPLE_GROUP:
            # Append argument to list ...
            return strip_simplecdata(item)

        # Handle structs
        if itemtype.GROUP == STRUCT_GROUP:
            # Reclusively call this routine for packing structs
            return self._pack_struct(item, itemtype)

        # Handle functions
        if itemtype.GROUP == FUNC_GROUP:
            # Packs functions and registers them at RPC server
            return self._pack_func(item, itemtype)

        # Handle everything else ...
        return None  # Just return None - will (hopefully) be overwritten by memsync

    def _pack_array(self, array: Any, arraytype: Definition, start: int = 0) -> Any:
        """
        Recursive function, packing one dimension per call

        Args:
            - array: raw argument / return array, n-dimensional
            - arraytype: zugbruecke argtype / restype definition
            - start: dimension to start with when packing
        Returns:
            Packed argument / return array for shipping
        """

        for idx, flag in enumerate(arraytype.flags[start:], start = start):

            # Is pointer?
            if flag == FLAG_POINTER:
                # Strip pointer
                array = strip_pointer(array)

            # Is array dimension?
            elif flag > 0:
                # Only dive deeper if this is not the last flag
                if idx < len(arraytype.flags) - 1:
                    array = [
                        self._pack_array(
                            dim, arraytype, start=idx + 1
                        )
                        for dim in array[:]
                    ]
                else:
                    array = array[:]
                    if arraytype.GROUP == STRUCT_GROUP:
                        array = [
                            self._pack_struct(struct, arraytype) for struct in array
                        ]

            # Handle unknown flags
            else:
                raise DataFlagError("unknown non-pointer flag for array")

        return array

    def _pack_func(self, func: Callable, functype: Definition) -> Optional[str]:
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
                argtypes = functype.argtypes,
                restype = functype.restype,
                memsyncs = functype.memsyncs,
            )

        # Return name of callback entry
        return name

    def _pack_struct(self, struct: Any, structtype: Definition) -> List[Tuple[str, Any]]:
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
                name,
                self._pack_item(
                    getattr(struct, name), definition
                ),
            )
            for name, definition in structtype.fields
        ]

    def _sync_arg(self, old_arg: Any, new_arg: Any, argtype: Definition):
        """
        Args:
            - old_arg: Raw argument
            - new_arg: Raw argument
            - argtype: zugbruecke argtype definition
        Returns:
            Nothing
        """

        # The non-trivial case first, arrays
        if not argtype.is_scalar:
            # Sync items in array
            self._sync_array(old_arg, new_arg, argtype)
            # Leave
            return

        # Do not do this for void pointers, likely handled by memsync
        if argtype.is_void:
            return

        # Strip away the pointers ... (all flags are pointers in this case)
        for flag in argtype.flags:
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            old_arg = strip_pointer(old_arg)
            new_arg = strip_pointer(new_arg)

        if argtype.GROUP == SIMPLE_GROUP:
            if hasattr(old_arg, "value"):
                old_arg.value = new_arg.value
            else:
                pass  # only relevant within structs or for actual pointers to scalars
            return

        if argtype.GROUP == STRUCT_GROUP:
            self._sync_struct(old_arg, new_arg, argtype)
            return

        if argtype.GROUP == FUNC_GROUP:
            return  # Nothing to do?

        raise DataGroupError("unexpected datatype group")

    def _sync_array(self, old_array: Any, new_array: Any, arraytype: Definition, start: int = 0):
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

        for idx, flag in enumerate(arraytype.flags[start:], start = start):

            # Handle pointers
            if flag == FLAG_POINTER:
                old_array = strip_pointer(old_array)
                new_array = strip_pointer(new_array)

            # Handle arrays
            elif flag > 0:
                # Only dive deeper if this is not the last flag
                if idx < len(arraytype.flags) - 1:
                    for old_dim, new_dim in zip(old_array[:], new_array[:]):
                        self._sync_array(
                            old_dim,
                            new_dim,
                            arraytype,
                            start=idx + 1,
                        )
                else:
                    if arraytype.GROUP == SIMPLE_GROUP:
                        # HACK can not overwrite immutable bytes & strings, skipping sync operation.
                        # Relevant for fixed-length char & wchar arrays by value in structs.
                        if not isinstance(old_array, bytes) and not isinstance(old_array, str):
                            old_array[:] = new_array[:]
                    elif arraytype.GROUP == STRUCT_GROUP:
                        for old_struct, new_struct in zip(old_array[:], new_array[:]):
                            self._sync_struct(
                                old_struct, new_struct, arraytype
                            )
                    elif arraytype.GROUP == FUNC_GROUP:
                        raise NotImplementedError(
                            "functions in arrays are not supported"
                        )
                    else:
                        raise DataGroupError("unexpected datatype group")

            # Handle unknown flags
            else:
                raise DataFlagError("unknown non-pointer flag for array")

    def _sync_struct(self, old_struct: Any, new_struct: Any, structtype: Definition):
        """
        Args:
            - old_struct: raw argument struct
            - new_struct: raw argument struct
            - structtype: zugbruecke argtype definition
        Returns:
            Nothing
        """

        # Step through arguments
        for name, definition in structtype.fields:
            self._sync_arg(
                getattr(old_struct, name),
                getattr(new_struct, name),
                definition,
            )

    def _unpack_item(self, item: Any, itemtype: Definition) -> Any:
        """
        Args:
            - item: packaged argument / return value from shipping
            - itemtype: zugbruecke argtype / restype definition
        Returns:
            Raw argument / return value
        """

        # The non-trivial case first, arrays
        if not itemtype.is_scalar:
            # Unpack items in array
            _, item = self._unpack_array(item, itemtype)
            return item

        # Handle voids (likely mensync stuff)
        if itemtype.is_void:
            # Return a placeholder
            return None
        # Handle fundamental types
        elif itemtype.GROUP == SIMPLE_GROUP:
            item = itemtype.base_type(item)
        # Handle structs
        elif itemtype.GROUP == STRUCT_GROUP:
            item = self._unpack_struct(item, itemtype)
        # Handle functions
        elif itemtype.GROUP == FUNC_GROUP:
            item = self._unpack_func(item, itemtype)
        # Handle everything else ...
        else:
            raise DataGroupError("unexpected datatype group")

        # Step through flags in reverse order (if it's not a memsync field)
        for flag in reversed(itemtype.flags):
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            item = ctypes.pointer(item)

        return item

    def _unpack_array(self, array: Any, arraytype: Definition, start: int = 0) -> Tuple[Any, Any]:
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
        flag = arraytype.flags[start]

        # Dive deeper?
        if start < len(arraytype.flags) - 1:

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

            if arraytype.GROUP == SIMPLE_GROUP:
                subtype = arraytype.base_type * flag
                array = subtype(*array)
            elif arraytype.GROUP == STRUCT_GROUP:
                subtype = arraytype.base_type * flag
                array = subtype(
                    *(self._unpack_struct(dim, arraytype) for dim in array)
                )
            elif arraytype.GROUP == FUNC_GROUP:
                raise NotImplementedError("functions in arrays are not supported")
            else:
                raise DataGroupError("unexpected datatype group")

        return subtype, array

    def _unpack_func(self, name: Optional[str], functype: Definition) -> Optional[Callable]:
        """
        Args:
            - name: (Generated) name of func from shipping
            - functype: zugbruecke argtype / restype definition
        Returns:
            Callable
        """

        # HACK if this function is called on the client, just return None
        if not self._is_server:
            return None

        # Has callback translator not been built yet?
        if name not in self._cache.handle.keys():

            # Generate, decorate and store callback translator in cache
            self._cache.handle[name] = functype.base_type(
                CallbackServer(
                    name = name,
                    rpc_client = self._callback_client,
                    data = self,
                    log = self._log,
                    argtypes = functype.argtypes,
                    restype = functype.restype,
                    memsyncs = functype.memsyncs,
                )
            )

        # Return name of callback entry
        return self._cache.handle[name]

    def _unpack_struct(self, struct: Any, structtype: Definition) -> Any:
        """
        Args:
            struct: Packed struct from shipping
            structtype: zugbruecke argtype / restype definition
        Returns:
            Raw struct object
        """

        # Generate new instance of struct datatype
        new_struct = structtype.base_type()

        # Step through arguments
        for (name, packed_value), (_, definition) in zip(struct, structtype.fields):

            # HACK if value is None, it's likely a function pointer sent back from Wine side - skip
            if packed_value is None:
                continue

            value = self._unpack_item(packed_value, definition)

            try:

                if all((
                    definition.base_type in (ctypes.c_char, ctypes.c_wchar),
                    not definition.is_pointer,
                    not definition.is_scalar,
                )):

                    setattr(
                        new_struct,  # struct instance to be modified
                        name,  # field name
                        value.value,  # field value
                    )

                else:

                    setattr(
                        new_struct,  # struct instance to be modified
                        name,  # field name
                        value,  # field value
                    )

            except TypeError:  # TODO HACK relevant for structs & callbacks & memsync together

                self._log.error(name, value, type(value))

                setattr(
                    new_struct,  # struct instance to be modified
                    name,  # field name
                    ctypes.cast(value, ctypes.c_void_p),
                )

        return new_struct
