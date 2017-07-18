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
# IMPORT: Unix ctypes members, which will be modified
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import cdll as __cdll__
from ctypes import CDLL as __CDLL__
from ctypes import LibraryLoader as __LibraryLoader__

from ctypes import CFUNCTYPE as __CFUNCTYPE__
from ctypes import _c_functype_cache as __c_functype_cache__


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: zugbruecke core
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .core.session_client import session_client_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, currently stubbed in zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def DllCanUnloadNow(): # EXPORT
	pass # TODO stub

def DllGetClassObject(rclsid, riid, ppv): # EXPORT
	pass # TODO stub

def FormatError(error_code = None): # EXPORT
	pass # TODO stub

def GetLastError(): # EXPORT
	pass # TODO stub

class HRESULT: # EXPORT
	pass # TODO stub

def WINFUNCTYPE(restype, *argtypes, **kw): # EXPORT
	pass # TODO stub

def WinError(code = None, descr = None): # EXPORT
	pass # TODO stub

def _check_HRESULT(result): # EXPORT
	pass # TODO stub

# Used in ctypes __init__.py by WINFUNCTYPE. Needs to be exposed?
_win_functype_cache = {} # EXPORT # TODO stub

def get_last_error(): # EXPORT
	pass # TODO stub

def set_last_error(last_error): # EXPORT
	pass # TODO stub


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Routines only availabe on Wine / Windows, provided via zugbruecke
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Start new zugbruecke session
current_session = session_client_class()

# Need to handle c functions in DLLs
CFUNCTYPE = __CFUNCTYPE__ # EXPORT
_c_functype_cache = __c_functype_cache__ # EXPORT

# Just in case ...
_FUNCFLAG_STDCALL = 0 # EXPORT

# EXPORT: Wrapper for CDLL class
def CDLL(
	name, mode = DEFAULT_MODE, handle = None,
	use_errno = False,
	use_last_error = False
	):

	# If there is a handle to a zugbruecke session, return session
	if handle is not None:
		if type(handle).__name__.startswith('zugbruecke'):
			return handle

	if handle is None and False: # TODO
		# If handle is none and name points to Wine library
		pass
	else:
		# If Unix library, return CDLL class instance
		return __CDLL__(name, mode, handle, use_errno, use_last_error)


# CDLL
cdll = __cdll__ # EXPORT

class zugbruecke_cdll_class():


	pass


class zugbruecke_windll_class(): # Mimic ctypes.windll


	def __init__(self, session):

		self.__session__ = session


	def LoadLibrary(self, name):

		# Return a DLL instance object from within the session
		return self.__session__.load_library(dll_name = name, dll_type = 'windll')


class oledll: # EXPORT
	pass # TODO stub

class OleDLL: # EXPORT
	pass # TODO stub

# Set up and expose windll, prepare (but do not start) session while doing so
windll = zugbruecke_windll_class(current_session) # EXPORT

class WinDLL: # EXPORT
	pass # TODO stub

# LibraryLoader
LibraryLoader = __LibraryLoader__ # EXPORT # stub
