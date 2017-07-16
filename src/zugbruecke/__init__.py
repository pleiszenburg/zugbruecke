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
# IMPORT: Unix ctypes members, which will NOT be modified
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
	_c_functype_cache,
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
	CFUNCTYPE,
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
# IMPORT: Unix ctypes members, which WILL be modified
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import cdll as __cdll__
from ctypes import CDLL as __CDLL__
from ctypes import LibraryLoader as __LibraryLoader__


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Wine ctypes from zugbruecke core
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Load windll_class for mimicing ctypes.windll eventually, make it private
from ._windll_ import windll_class as __windll_class__

# Expose session class for advanced users and tests
from .core.session_client import session_client_class as session


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, currently stubbed in zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def DllCanUnloadNow():
	pass # TODO stub

def DllGetClassObject(rclsid, riid, ppv):
	pass # TODO stub

def FormatError(error_code = None):
	pass # TODO stub

def GetLastError():
	pass # TODO stub

class HRESULT:
	pass # TODO stub

def WINFUNCTYPE(restype, *argtypes, **kw):
	pass # TODO stub

def WinError(code = None, descr = None):
	pass # TODO stub

def _check_HRESULT(result):
	pass # TODO stub

# Used in ctypes __init__.py by WINFUNCTYPE. Needs to be exposed?
_win_functype_cache = {} # TODO stub

def get_last_error():
	pass # TODO stub

def set_last_error(last_error):
	pass # TODO stub


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, provided via zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Just in case ...
_FUNCFLAG_STDCALL = 0

# CDLL
cdll = __cdll__
CDLL = __CDLL__ # stub, needs to figure out whether it is called with DLL or Unix lib

class oledll:
	pass # TODO stub

class OleDLL:
	pass # TODO stub

# Set up and expose windll, prepare (but do not start) session while doing so
windll = __windll_class__()

class WinDLL:
	pass # TODO stub

# LibraryLoader
LibraryLoader = __LibraryLoader__ # stub
