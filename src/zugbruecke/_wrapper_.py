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
# IMPORT: Unix ctypes members, which will be modified
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import cdll as __cdll__
from ctypes import CDLL as __CDLL__
from ctypes import LibraryLoader as __LibraryLoader__


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: zugbruecke core
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ._windll_ import windll_class as __windll_class__


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
