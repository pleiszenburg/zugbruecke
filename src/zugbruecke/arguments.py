# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/arguments.py: (Un-) packing of arguments & their definitions

	Required to run on platform / side: [UNIX, WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
#from pprint import pformat as pf

try:
	from .const import (
		FLAG_POINTER,
		GROUP_VOID,
		GROUP_FUNDAMENTAL,
		GROUP_STRUCT
		)
except:
	from const import (
		FLAG_POINTER,
		GROUP_VOID,
		GROUP_FUNDAMENTAL,
		GROUP_STRUCT
		)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES: Definition packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def pack_definition_argtypes(argtypes):

	return [__pack_definition_dict__(arg) for arg in argtypes]


def pack_definition_returntype(restype):

	return __pack_definition_dict__(restype)


def __pack_definition_dict__(datatype, field_name = None):

	# Not all datatypes have a name, let's handle that
	type_name = None
	# Get name of datatype, such as c_int, if there is one
	if hasattr(datatype, '__name__'):
		type_name = datatype.__name__

	# Get group of datatype
	group_name = type(datatype).__name__ # 'PyCSimpleType', 'PyCStructType', PyCArrayType or 'PyCPointerType'

	# List of flags: Pointer flag or length of array (one entry per dimension)
	flag_list = []

	# Strip away all pointers and arrays until simple type or struct type is left & keep order
	while group_name in ['PyCPointerType', 'PyCArrayType']:

		# Catch pointer
		if group_name == 'PyCPointerType':

			# Append pointer flag to list of flags
			flag_list.append(FLAG_POINTER)

		# Catch arrays
		elif group_name == 'PyCArrayType':

			# Append length to flag list
			flag_list.append(datatype._length_)

		# This is not supposed to happen ...
		else:

			raise

		# Get next type in sequence
		datatype = datatype._type_

		# Get type and group name of next type in sequence
		type_name = datatype.__name__
		group_name = type(datatype).__name__

	# Fundamental ('simple') C types
	if group_name == 'PyCSimpleType':

		return {
			'f': flag_list,
			'n': field_name, # kw
			't': type_name, # Type name, such as 'c_int'
			'g': GROUP_FUNDAMENTAL
			}

	# Structs
	elif group_name == 'PyCStructType':

		return {
			'f': flag_list,
			'n': field_name, # kw
			't': type_name, # Type name, such as 'c_int'
			'g': GROUP_STRUCT,
			'_fields_': [
				__pack_definition_dict__(field[1], field[0]) for field in datatype._fields_
				]
			}

	# UNKNOWN stuff, likely pointers - handled without datatype
	else:

		return {
			'f': flag_list,
			'n': field_name, # kw
			't': type_name, # Type name, such as 'c_int'
			'g': GROUP_VOID # Let's try void
			}
