# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/__init__.py: Module init file

	Required to run on platform / side: [UNIX]

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
# IMPORT: Unix ctypes members, which will not be modified - directly from ctypes
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import __version__

from ctypes import (
	_CFuncPtr,
	_FUNCFLAG_CDECL,
	_FUNCFLAG_PYTHONAPI,
	_FUNCFLAG_USE_ERRNO,
	_FUNCFLAG_USE_LASTERROR,
	_Pointer,
	_SimpleCData,
	_calcsize,
	_cast,
	_cast_addr,
	_check_size,
	_ctypes_version,
	_dlopen, # behaviour depends on platform
	_endian,
	_memmove_addr,
	_memset_addr,
	_pointer_type_cache,
	_reset_cache,
	_string_at,
	_string_at_addr,
	_wstring_at,
	_wstring_at_addr
	)

from ctypes import (
	ARRAY, # Python 3.6: Deprecated XXX
	ArgumentError,
	Array,
	BigEndianStructure,
	DEFAULT_MODE,
	LittleEndianStructure,
	POINTER,
	PYFUNCTYPE,
	PyDLL,
	RTLD_GLOBAL,
	RTLD_LOCAL,
	SetPointerType, # Python 3.6: Deprecated XXX
	Structure,
	Union,
	addressof,
	alignment,
	byref,
	c_bool,
	c_buffer,
	c_byte,
	c_char,
	c_char_p,
	c_double,
	c_float,
	c_int,
	c_int16,
	c_int32,
	c_int64,
	c_int8,
	c_long,
	c_longdouble,
	c_longlong,
	c_short,
	c_size_t,
	c_ssize_t,
	c_ubyte,
	c_uint,
	c_uint16,
	c_uint32,
	c_uint64,
	c_uint8,
	c_ulong,
	c_ulonglong,
	c_ushort,
	c_void_p,
	c_voidp,
	c_wchar,
	c_wchar_p,
	cast,
	create_string_buffer,
	create_unicode_buffer,
	get_errno,
	memmove,
	memset,
	pointer,
	py_object,
	pydll,
	pythonapi,
	resize,
	set_errno,
	sizeof,
	string_at,
	wstring_at
	)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: ctypes members, which will be modified - from zugbruecke wrapper
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ._wrapper_ import (
	_FUNCFLAG_STDCALL,
	cdll,
	CDLL,
	oledll,
	OleDLL,
	windll,
	WinDLL,
	LibraryLoader,
	DllCanUnloadNow,
	DllGetClassObject,
	FormatError,
	GetLastError,
	HRESULT,
	CFUNCTYPE,
	WINFUNCTYPE,
	WinError,
	_check_HRESULT,
	_c_functype_cache,
	_win_functype_cache,
	get_last_error,
	set_last_error
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: zugbruecke core
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Expose session class for advanced users and tests
from .core.session_client import session_client_class as session

# Expose current session and Wine API
from ._wrapper_ import (
	current_session,
	wine
	)
