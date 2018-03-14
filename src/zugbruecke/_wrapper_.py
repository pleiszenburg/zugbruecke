# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/_wrapper_.py: Patches platform-specific ctypes features

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
# IMPORT: Unix ctypes members required by wrapper
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import DEFAULT_MODE


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Unix ctypes members, which will exported as they are
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import (
	_c_functype_cache,
	_CFuncPtr,
	_FUNCFLAG_USE_ERRNO,
	_FUNCFLAG_USE_LASTERROR,
	CFUNCTYPE,
	LibraryLoader
	)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Unix ctypes members, which will be modified
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import CDLL as ctypes_CDLL_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: zugbruecke core
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .core.session_client import session_client_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, currently stubbed in zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def DllCanUnloadNow(): # EXPORT
	pass # TODO stub - required for COM

def DllGetClassObject(rclsid, riid, ppv): # EXPORT
	pass # TODO stub - required for COM

class HRESULT: # EXPORT
	pass # TODO stub - special form of c_long, will require changes to argument parser

def _check_HRESULT(result): # EXPORT
	pass # TODO stub - method for HRESULT, checks error bit, raises error if true. Needs reimplementation.


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# zugbruecke session
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Start new zugbruecke session
current_session = session_client_class() # EXPORT


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows - accessed via server
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

FormatError = current_session.ctypes_FormatError # EXPORT

get_last_error = current_session.ctypes_get_last_error # EXPORT

GetLastError = current_session.ctypes_GetLastError # EXPORT

set_last_error = current_session.ctypes_set_last_error # EXPORT

WinError = current_session.ctypes_WinError # EXPORT


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CFUNCTYPE & WINFUNCTYPE
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# TODO Compatibility to CFUNCTYPE on Wine side must be implemented

# Required for WINFUNCTYPE
_FUNCFLAG_STDCALL = 0 # EXPORT

# CFUNCTYPE
# _c_functype_cache

# WINDLL function calls
def WINFUNCTYPE(restype, *argtypes, **kw): # EXPORT
	flags = _FUNCFLAG_STDCALL
	if kw.pop("use_errno", False):
		flags |= _FUNCFLAG_USE_ERRNO
	if kw.pop("use_last_error", False):
		flags |= _FUNCFLAG_USE_LASTERROR
	if kw:
		raise ValueError("unexpected keyword argument(s) %s" % kw.keys())
	try:
		return _win_functype_cache[(restype, argtypes, flags)]
	except KeyError:
		class WinFunctionType(_CFuncPtr):
			_argtypes_ = argtypes
			_restype_ = restype
			_flags_ = flags
		_win_functype_cache[(restype, argtypes, flags)] = WinFunctionType
		return WinFunctionType

if WINFUNCTYPE.__doc__:
	WINFUNCTYPE.__doc__ = CFUNCTYPE.__doc__.replace('CFUNCTYPE', 'WINFUNCTYPE')

# Used in ctypes __init__.py by WINFUNCTYPE
_win_functype_cache = {} # EXPORT


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Wine-related stuff
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wine:

	unix_to_wine = current_session.path_unix_to_wine
	wine_to_unix = current_session.path_wine_to_unix


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, provided via zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# EXPORT: Wrapper for CDLL class
def CDLL(
	name, mode = DEFAULT_MODE, handle = None,
	use_errno = False,
	use_last_error = False
	):

	# If there is a handle to a zugbruecke session, return session
	if handle is not None:

		# Handle zugbruecke handle
		if type(handle).__name__ == 'dll_client_class':

			# Return it as-is TODO what about a new name?
			return handle

		# Handle ctypes handle
		else:

			# Return ctypes DLL class instance, let it handle the handle as it would
			return ctypes_CDLL_class(name, mode, handle, use_errno, use_last_error)

	# If no handle was passed, it's a new library
	else:

		# Let's try the Wine side first
		try:

			# Return a handle on dll_client object
			return current_session.load_library(
				dll_name = name, dll_type = 'cdll', dll_param = {
					'mode': mode, 'use_errno': use_errno, 'use_last_error': use_last_error
					}
				)

		# Well, it might be a Unix library after all
		except:

			# If Unix library, return CDLL class instance
			return ctypes_CDLL_class(name, mode, handle, use_errno, use_last_error)


def WinDLL(
	name, mode = DEFAULT_MODE, handle = None,
	use_errno = False,
	use_last_error = False
	): # EXPORT

	return current_session.load_library(
		dll_name = name, dll_type = 'windll', dll_param = {
			'mode': mode, 'use_errno': use_errno, 'use_last_error': use_last_error
			}
		)


def OleDLL(
	name, mode = DEFAULT_MODE, handle = None,
	use_errno = False,
	use_last_error = False
	): # EXPORT

	return current_session.load_library(
		dll_name = name, dll_type = 'oledll', dll_param = {
			'mode': mode, 'use_errno': use_errno, 'use_last_error': use_last_error
			}
		)


# Set up and expose dll library loader objects
cdll = LibraryLoader(CDLL) # EXPORT
windll = LibraryLoader(WinDLL) # EXPORT
oledll = LibraryLoader(OleDLL) # EXPORT
