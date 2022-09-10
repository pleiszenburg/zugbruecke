# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/arg_definition.py: (Un-) packing of argument definitions

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

from ..const import (
    _FUNCFLAG_STDCALL,
    FLAG_POINTER,
    GROUP_VOID,
    GROUP_FUNDAMENTAL,
    GROUP_STRUCT,
    GROUP_FUNCTION,
)
from ..errors import DataFlagError, DataTypeError


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Definition packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class arguments_definition_class:
    def generate_callback_decorator(self, flags, restype, *argtypes, **kwargs):

        _memsync_ = kwargs.pop("memsync", [])

        if not (flags & _FUNCFLAG_STDCALL):
            func_type_key = _FUNCFLAG_CDECL
        else:
            func_type_key = _FUNCFLAG_STDCALL

        try:

            # There already is a matching function pointer type available
            return self.cache_dict["func_type"][func_type_key][
                (restype, argtypes, flags)
            ]

        except KeyError:

            # Create new function pointer type class
            class FunctionType(ctypes._CFuncPtr):
                _argtypes_ = argtypes
                _restype_ = restype
                memsync = self.unpack_definition_memsync(_memsync_)
                _flags_ = flags

            # Store the new type and return
            self.cache_dict["func_type"][func_type_key][
                (restype, argtypes, flags)
            ] = FunctionType
            return FunctionType

    def pack_definition_argtypes(self, argtypes):

        return [self.__pack_definition_dict__(arg) for arg in argtypes]

    def pack_definition_returntype(self, restype):

        return self.__pack_definition_dict__(restype)

    def unpack_definition_argtypes(self, argtypes_d):

        return [
            self.__unpack_definition_dict__(arg_d_dict) for arg_d_dict in argtypes_d
        ]

    def unpack_definition_returntype(self, restype_d):

        return self.__unpack_definition_dict__(restype_d)

    def __generate_struct_from_definition__(self, struct_d_dict):

        # Prepare fields
        fields = []

        # Step through fields
        for field in struct_d_dict["_fields_"]:

            # Handle fundamental C datatypes (PyCSimpleType)
            if field["g"] == GROUP_FUNDAMENTAL:

                # Add tuple with name and fundamental datatype
                fields.append(
                    (field["n"], self.__unpack_definition_fundamental_dict__(field))
                )

            # Structures (PyCStructType)
            elif field["g"] == GROUP_STRUCT:

                # Add tuple with name and struct datatype
                fields.append(
                    (field["n"], self.__unpack_definition_struct_dict__(field))
                )

            # Functions (PyCFuncPtrType)
            elif field["g"] == GROUP_FUNCTION:

                # Add tuple with name and struct datatype
                fields.append(
                    (field["n"], self.__unpack_definition_function_dict__(field))
                )

            # Handle generic pointers
            elif field["g"] == GROUP_VOID:

                fields.append(
                    (
                        field["n"],
                        self.__unpack_definition_flags__(
                            ctypes.c_void_p, field["f"], is_void_pointer=True
                        ),
                    )
                )

            # Undhandled stuff (pointers of pointers etc.) TODO
            else:

                # HACK TODO
                fields.append((field["n"], ctypes.c_int))

        # Generate actual class
        self.cache_dict["struct_type"][struct_d_dict["t"]] = type(
            struct_d_dict["t"],  # Potenial BUG: Ends up in __main__ scope, problematic?
            (ctypes.Structure,),
            {"_fields_": fields},
        )

    def __pack_definition_dict__(self, datatype, field_name=None):

        # Get name of datatype, such as c_int, if there is one, else None
        type_name = getattr(datatype, "__name__", None)

        # Get group of datatype
        group_name = type(datatype).__name__
        # Can be: 'PyCSimpleType', 'PyCStructType', 'PyCArrayType' or 'PyCPointerType'

        # List of flags: Pointer flag or length of array (one entry per dimension)
        flag_list = []

        # Strip away all pointers and arrays until simple type or struct type is left & keep order
        while group_name in ["PyCPointerType", "PyCArrayType"]:

            # Catch pointer
            if group_name == "PyCPointerType":

                # Append pointer flag to list of flags
                flag_list.append(FLAG_POINTER)

            # Catch arrays
            elif group_name == "PyCArrayType":

                # Append length to flag list
                flag_list.append(datatype._length_)

            # This is not supposed to happen ...
            else:

                raise DataTypeError("unknown ctypes wrapper type")

            # Get next type in sequence
            datatype = datatype._type_

            # Get type and group name of next type in sequence
            type_name = datatype.__name__
            group_name = type(datatype).__name__

        # Store the depth of arrays (arrays within arrays etc; for speed)
        flag_array_depth = len([flag for flag in flag_list if flag > 0])

        # Flag pure scalars as, well, pure scalars (for speed)
        flag_scalar = flag_array_depth == 0

        # Flag elements containing pointers
        flag_pointer = len([flag for flag in flag_list if flag == FLAG_POINTER]) != 0

        # Fundamental ('simple') C types
        if group_name == "PyCSimpleType":

            return {
                "f": flag_list,
                "s": flag_scalar,
                "d": flag_array_depth,
                "p": flag_pointer,
                "n": field_name,  # kw
                "t": type_name,  # Type name, such as 'c_int'
                "g": GROUP_FUNDAMENTAL,
            }

        # Structs
        elif group_name == "PyCStructType":

            # HACK Different struct types from different name spaces can have identical names
            _type_name = type_name + "@" + str(id(datatype))

            # Keep track of datatype on client side
            if _type_name not in self.cache_dict["struct_type"].keys():
                self.cache_dict["struct_type"][_type_name] = datatype

            # TODO: For speed, cache packed struct definitions for known structs

            return {
                "f": flag_list,
                "s": flag_scalar,
                "d": flag_array_depth,
                "p": flag_pointer,
                "n": field_name,  # kw
                "t": _type_name,  # Type name, such as 'c_int'
                "g": GROUP_STRUCT,
                "_fields_": [
                    self.__pack_definition_dict__(field[1], field[0])
                    for field in datatype._fields_
                ],
            }

        # Function pointers
        elif group_name == "PyCFuncPtrType":

            # TODO: For speed, cache packed function definitions for known functions

            return {
                "f": flag_list,
                "s": flag_scalar,
                "d": flag_array_depth,
                "p": flag_pointer,
                "n": field_name,  # kw
                "t": (
                    datatype._restype_,
                    datatype._argtypes_,
                    datatype._flags_,
                ).__hash__(),
                "g": GROUP_FUNCTION,
                "_argtypes_": self.pack_definition_argtypes(datatype._argtypes_),
                "_restype_": self.pack_definition_returntype(datatype._restype_),
                "_memsync_": self.pack_definition_memsync(datatype.memsync),
                "_flags_": datatype._flags_,
            }

        # UNKNOWN stuff, likely pointers - handled without datatype
        else:

            return {
                "f": flag_list,
                "s": flag_scalar,
                "d": flag_array_depth,
                "p": flag_pointer,
                "n": field_name,  # kw
                "t": type_name,  # Type name, such as 'c_int'
                "g": GROUP_VOID,  # Let's try void
            }

    def __unpack_definition_dict__(self, datatype_d_dict):

        # Handle fundamental C datatypes (PyCSimpleType)
        if datatype_d_dict["g"] == GROUP_FUNDAMENTAL:

            return self.__unpack_definition_fundamental_dict__(datatype_d_dict)

        # Structures (PyCStructType)
        elif datatype_d_dict["g"] == GROUP_STRUCT:

            return self.__unpack_definition_struct_dict__(datatype_d_dict)

        # Function pointers (PyCFuncPtrType)
        elif datatype_d_dict["g"] == GROUP_FUNCTION:

            return self.__unpack_definition_function_dict__(datatype_d_dict)

        # Handle generic pointers
        elif datatype_d_dict["g"] == GROUP_VOID:

            return self.__unpack_definition_flags__(
                ctypes.c_void_p, datatype_d_dict["f"], is_void_pointer=True
            )

        # Undhandled stuff (pointers of pointers etc.) TODO
        else:

            # HACK TODO
            return self.__unpack_definition_flags__(
                ctypes.c_int, datatype_d_dict["f"]  # HACK let's assume int  # flags
            )

    def __unpack_definition_flags__(self, datatype, flag_list, is_void_pointer=False):

        # Re-create arrays and pointers
        for flag_index, flag in enumerate(reversed(flag_list)):
            if flag > 0:  # array
                datatype = datatype * flag
            elif flag == FLAG_POINTER:
                if not is_void_pointer:  # do this only for last flag TODO
                    datatype = ctypes.POINTER(datatype)
            else:
                raise DataFlagError("unknown non-pointer flag for array")

        return datatype

    def __unpack_definition_function_dict__(self, datatype_d_dict):

        # TODO BUG only works on Wine Python, must not be called on Unix side
        if not self.is_server:
            raise SystemError("method must not be called on Unix/client side")

        # Generate function pointer type (used as parameter type and as decorator for Python function)
        factory_type = self.generate_callback_decorator(
            datatype_d_dict["_flags_"],
            self.unpack_definition_returntype(datatype_d_dict["_restype_"]),
            *self.unpack_definition_argtypes(datatype_d_dict["_argtypes_"]),
            memsync=self.unpack_definition_memsync(datatype_d_dict["_memsync_"]),
        )

        # Store function pointer type for subsequent use as decorator
        datatype_d_dict["_factory_type_"] = factory_type

        return factory_type

    def __unpack_definition_fundamental_dict__(self, datatype_d_dict):

        # Return type class or type pointer
        return self.__unpack_definition_flags__(
            getattr(ctypes, datatype_d_dict["t"]),
            datatype_d_dict["f"],
            datatype_d_dict["t"] == "c_void_p",
        )

    def __unpack_definition_struct_dict__(self, datatype_d_dict):

        # Generate struct class if it does not exist yet
        if datatype_d_dict["t"] not in self.cache_dict["struct_type"].keys():
            self.__generate_struct_from_definition__(datatype_d_dict)

        # Return type class or type pointer
        return self.__unpack_definition_flags__(
            self.cache_dict["struct_type"][datatype_d_dict["t"]],  # struct class
            datatype_d_dict["f"],  # flags
        )
