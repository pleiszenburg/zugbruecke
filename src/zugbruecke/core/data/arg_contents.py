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
from typing import Any, Dict, List, Optional, Tuple

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
                self.__pack_item__(arg, argtype)
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
                self.__pack_item__(arg, argtype)
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
                self.__unpack_item__(arg, argtype)
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
                self.__unpack_item__(arg, argtype)
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

        return self.__pack_item__(value, restype)

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
            return self.__unpack_item__(value, restype)

        # The original ctypes strips away ctypes datatypes for fundamental
        # (non-pointer, non-struct) return values and returns plain Python
        # data types instead - the unpacked result requires stripping
        return self.__item_value_strip__(
            self.__unpack_item__(value, restype)
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
            self.__sync_item__(old_arg, new_arg, argtype)

    def __item_pointer_strip__(self, arg_in):

        # Handle pointer object
        if hasattr(arg_in, "contents"):
            return arg_in.contents
        # Handle reference (byref) 'light pointer'
        elif hasattr(arg_in, "_obj"):
            return arg_in._obj
        # Object was likely not provided as a pointer
        else:
            return arg_in

    def __item_value_strip__(self, arg_in):

        return getattr(arg_in, "value", arg_in)

    def __pack_item__(self, arg_in, arg_def_dict):

        # The non-trivial case first, non-scalars: arrays
        if not arg_def_dict["s"]:
            # Unpack every item in array
            return self.__pack_item_array__(arg_in, arg_def_dict)

        # Strip away the pointers ... (all flags are pointers in this case)
        for flag in arg_def_dict["f"]:
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            if is_null_pointer(arg_in):
                # Just return None - will (hopefully) be overwritten by memsync
                return None
            arg_in = self.__item_pointer_strip__(arg_in)

        # Handle fundamental types
        if arg_def_dict["g"] == GROUP_FUNDAMENTAL:
            # Append argument to list ...
            return self.__item_value_strip__(arg_in)
        # Handle structs
        elif arg_def_dict["g"] == GROUP_STRUCT:
            # Reclusively call this routine for packing structs
            return self.__pack_item_struct__(arg_in, arg_def_dict)
        # Handle functions
        elif arg_def_dict["g"] == GROUP_FUNCTION:
            # Packs functions and registers them at RPC server
            return self.__pack_item_function__(arg_in, arg_def_dict)
        # Handle everything else ... likely pointers handled by memsync
        else:
            # Just return None - will (hopefully) be overwritten by memsync
            return None

    def __pack_item_array__(self, arg_in, arg_def_dict, flag_index_start=0):

        for flag_index in range(flag_index_start, len(arg_def_dict["f"])):

            # Extract the flag
            flag = arg_def_dict["f"][flag_index]

            # Handle pointers
            if flag == FLAG_POINTER:

                arg_in = self.__item_pointer_strip__(arg_in)

            # Handle arrays
            elif flag > 0:

                # Only dive deeper if this is not the last flag
                if flag_index < len(arg_def_dict["f"]) - 1:
                    arg_in = [
                        self.__pack_item_array__(
                            e, arg_def_dict, flag_index_start=flag_index + 1
                        )
                        for e in arg_in[:]
                    ]
                else:
                    arg_in = arg_in[:]
                    if arg_def_dict["g"] == GROUP_STRUCT:
                        arg_in = [
                            self.__pack_item_struct__(e, arg_def_dict) for e in arg_in
                        ]

            # Handle unknown flags
            else:

                raise DataFlagError("unknown non-pointer flag for array")

        return arg_in

    def __pack_item_function__(self, func_ptr, func_def_dict):

        # HACK if on server, just return None
        if self._is_server:
            return None

        # Use memory address of function pointer as unique name/ID
        func_name = "func_%x" % id(func_ptr)

        # Has callback translator been built before?
        if func_name in self._cache.handle.keys():

            # Just return its name
            return func_name

        # Generate and store callback in cache
        self._cache.handle[func_name] = CallbackClient(
            name = func_name,
            handler = func_ptr,
            rpc_server = self._callback_server,
            data = self,
            log = self._log,
            argtypes_d = func_def_dict["_argtypes_"],
            restype_d = func_def_dict["_restype_"],
            memsync_d = self.unpack_definition_memsync(func_def_dict["_memsync_"]),
        )

        # Return name of callback entry
        return func_name

    def __pack_item_struct__(self, struct_raw, struct_def_dict):

        # Return parameter message list - MUST WORK WITH PICKLE
        return [
            (
                field_def_dict["n"],
                self.__pack_item__(
                    getattr(struct_raw, field_def_dict["n"]), field_def_dict
                ),
            )
            for field_def_dict in struct_def_dict["_fields_"]
        ]

    def __sync_item__(self, old_arg, new_arg, arg_def_dict):

        # The non-trivial case first, arrays
        if not arg_def_dict["s"]:
            # Sync items in array
            self.__sync_item_array__(old_arg, new_arg, arg_def_dict)
            # Leave
            return

        # Do not do this for void pointers, likely handled by memsync
        if arg_def_dict["g"] == GROUP_VOID:
            return

        # Strip away the pointers ... (all flags are pointers in this case)
        for flag in arg_def_dict["f"]:
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            old_arg = self.__item_pointer_strip__(old_arg)
            new_arg = self.__item_pointer_strip__(new_arg)

        if arg_def_dict["g"] == GROUP_FUNDAMENTAL:
            if hasattr(old_arg, "value"):
                old_arg.value = new_arg.value
            else:
                pass  # only relevant within structs or for actual pointers to scalars
        elif arg_def_dict["g"] == GROUP_STRUCT:
            return self.__sync_item_struct__(old_arg, new_arg, arg_def_dict)
        elif arg_def_dict["g"] == GROUP_FUNCTION:
            pass  # Nothing to do?
        else:
            raise DataGroupError("unexpected datatype group")

    def __sync_item_array__(self, old_arg, new_arg, arg_def_dict, flag_index_start=0):

        for flag_index in range(flag_index_start, len(arg_def_dict["f"])):

            # Extract the flag
            flag = arg_def_dict["f"][flag_index]

            # Handle pointers
            if flag == FLAG_POINTER:

                old_arg = self.__item_pointer_strip__(old_arg)
                new_arg = self.__item_pointer_strip__(new_arg)

            # Handle arrays
            elif flag > 0:

                # Only dive deeper if this is not the last flag
                if flag_index < len(arg_def_dict["f"]) - 1:

                    for old_arg_e, new_arg_e in zip(old_arg[:], new_arg[:]):
                        self.__sync_item_array__(
                            old_arg_e,
                            new_arg_e,
                            arg_def_dict,
                            flag_index_start=flag_index + 1,
                        )

                else:

                    if arg_def_dict["g"] == GROUP_FUNDAMENTAL:
                        old_arg[:] = new_arg[:]
                    elif arg_def_dict["g"] == GROUP_STRUCT:
                        for old_struct, new_struct in zip(old_arg[:], new_arg[:]):
                            self.__sync_item_struct__(
                                old_struct, new_struct, arg_def_dict
                            )
                    elif arg_def_dict["g"] == GROUP_FUNCTION:
                        raise NotImplementedError(
                            "functions in arrays are not supported"
                        )
                    else:
                        raise DataGroupError("unexpected datatype group")

            # Handle unknown flags
            else:

                raise DataFlagError("unknown non-pointer flag for array")

    def __sync_item_struct__(self, old_struct, new_struct, struct_def_dict):

        # Step through arguments
        for field_def_dict in struct_def_dict["_fields_"]:

            self.__sync_item__(
                getattr(old_struct, field_def_dict["n"]),
                getattr(new_struct, field_def_dict["n"]),
                field_def_dict,
            )

    def __unpack_item__(self, arg_raw, arg_def_dict):

        # The non-trivial case first, arrays
        if not arg_def_dict["s"]:
            # Unpack items in array
            return self.__unpack_item_array__(arg_raw, arg_def_dict)[1]

        # Handle fundamental types
        if arg_def_dict["g"] == GROUP_FUNDAMENTAL:
            arg_rebuilt = getattr(ctypes, arg_def_dict["t"])(arg_raw)
        # Handle structs
        elif arg_def_dict["g"] == GROUP_STRUCT:
            arg_rebuilt = self.__unpack_item_struct__(arg_raw, arg_def_dict)
        # Handle functions
        elif arg_def_dict["g"] == GROUP_FUNCTION:
            arg_rebuilt = self.__unpack_item_function__(arg_raw, arg_def_dict)
        # Handle voids (likely mensync stuff)
        elif arg_def_dict["g"] == GROUP_VOID:
            # Return a placeholder
            return None
        # Handle everything else ...
        else:
            raise DataGroupError("unexpected datatype group")

        # Step through flags in reverse order (if it's not a memsync field)
        for flag in reversed(arg_def_dict["f"]):
            if flag != FLAG_POINTER:
                raise DataFlagError("unknown non-pointer flag for scalar")
            arg_rebuilt = ctypes.pointer(arg_rebuilt)

        return arg_rebuilt

    def __unpack_item_array__(self, arg_in, arg_def_dict, flag_index=0):

        # Extract the flag
        flag = arg_def_dict["f"][flag_index]

        # Dive deeper?
        if flag_index < len(arg_def_dict["f"]) - 1:

            # Get index of next flag
            next_flag_index = flag_index + 1

            # If it's a Python list, dive once per element of list
            if type(arg_in) == list and flag != FLAG_POINTER:

                arg_in_tuple_list = [
                    self.__unpack_item_array__(
                        e, arg_def_dict, flag_index=next_flag_index
                    )
                    for e in arg_in
                ]
                arg_type = arg_in_tuple_list[0][0]
                arg_in = [e[1] for e in arg_in_tuple_list]

            # Likely a scalar or a ctypes object
            else:

                arg_type, arg_in = self.__unpack_item_array__(
                    arg_in, arg_def_dict, flag_index=next_flag_index
                )

            # Handle pointers
            if flag == FLAG_POINTER:
                arg_type = ctypes.POINTER(arg_type)
                arg_in = ctypes.pointer(arg_in)
            # Handle arrays
            elif flag > 0:
                arg_type = arg_type * flag
                arg_in = arg_type(*arg_in)
            # Handle unknown flags
            else:
                raise DataFlagError("unknown non-pointer flag for array")

        # No dive, we're at the bottom - just get the original ctypes type
        else:

            if flag == FLAG_POINTER:
                raise DataFlagError("unexpected pointer flag for array")

            if arg_def_dict["g"] == GROUP_FUNDAMENTAL:
                arg_type = getattr(ctypes, arg_def_dict["t"]) * flag
                arg_in = arg_type(*arg_in)
            elif arg_def_dict["g"] == GROUP_STRUCT:
                arg_type = self._cache.struct[arg_def_dict["t"]] * flag
                arg_in = arg_type(
                    *(self.__unpack_item_struct__(e, arg_def_dict) for e in arg_in)
                )
            elif arg_def_dict["g"] == GROUP_FUNCTION:
                raise NotImplementedError("functions in arrays are not supported")
            else:
                raise DataGroupError("unexpected datatype group")

        return arg_type, arg_in

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

            field_value = self.__unpack_item__(field_arg[1], field_def_dict)

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
