# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/session.py: A user-facing ctypes-drop-in-replacement session

    Required to run on platform / side: [UNIX]

    Copyright (C) 2017-2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
# IMPORT: Standard library
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from typing import Optional


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Original ctypes
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import ctypes as _ctypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: Unix ctypes members required by wrapper, which will exported as they are
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from ctypes import _FUNCFLAG_CDECL, DEFAULT_MODE, LibraryLoader


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT: zugbruecke core and missing ctypes flags
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from .abc import ConfigABC, CtypesSessionABC
from .session_client import SessionClient
from .const import _FUNCFLAG_STDCALL  # EXPORT
from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION CTYPES-DROP-IN-REPLACEMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class CtypesSession(CtypesSessionABC):

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # static components
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    DEFAULT_MODE = DEFAULT_MODE
    LibraryLoader = LibraryLoader
    _FUNCFLAG_CDECL = _FUNCFLAG_CDECL
    _FUNCFLAG_STDCALL = _FUNCFLAG_STDCALL

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # constructor
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def __init__(self, config: Optional[ConfigABC] = None):

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # zugbruecke session client and session interface
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Start new zugbruecke session
        self._zb_current_session = SessionClient(config=config)

        # Offer access to session internals
        self._zb_get_parameter = self._zb_current_session.get_parameter
        self._zb_set_parameter = self._zb_current_session.set_parameter
        self._zb_terminate = self._zb_current_session.terminate

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Routines only availabe on Wine / Windows - accessed via server
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self.FormatError = self._zb_current_session.FormatError

        self.get_last_error = self._zb_current_session.get_last_error

        self.GetLastError = self._zb_current_session.GetLastError

        self.set_last_error = self._zb_current_session.set_last_error

        self.WinError = self._zb_current_session.WinError

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Routines from ctypes.util
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        class _util:
            find_msvcrt = staticmethod(self._zb_current_session.find_msvcrt)
            find_library = staticmethod(self._zb_current_session.find_library)

        self._util = _util

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # CFUNCTYPE & WINFUNCTYPE
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # CFUNCTYPE and WINFUNCTYPE function pointer factories
        self.CFUNCTYPE = self._zb_current_session.CFUNCTYPE
        self.WINFUNCTYPE = self._zb_current_session.WINFUNCTYPE

        # Used as cache by CFUNCTYPE and WINFUNCTYPE
        self._c_functype_cache = self._zb_current_session.data.cache_dict["func_type"][
            _FUNCFLAG_CDECL
        ]
        self._win_functype_cache = self._zb_current_session.data.cache_dict[
            "func_type"
        ][_FUNCFLAG_STDCALL]

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Wine-related stuff
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self._zb_path_unix_to_wine = self._zb_current_session.path_unix_to_wine
        self._zb_path_wine_to_unix = self._zb_current_session.path_wine_to_unix

        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Set up and expose dll library loader objects
        # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Set up and expose dll library loader objects
        self.cdll = LibraryLoader(self.CDLL)
        self.windll = LibraryLoader(self.WinDLL)
        self.oledll = LibraryLoader(self.OleDLL)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # repr
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def __repr__(self):

        return '<CtypesSession arch={ARCH:s} build={BUILD:s}>'.format(
            ARCH = self._zb_current_session.config['arch'],
            BUILD = str(self._zb_current_session.config['pythonversion']),
        )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Allow readonly access to session states
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def _zb_id(self) -> str:
        return self._zb_current_session.id

    @property
    def _zb_client_up(self) -> bool:
        return self._zb_current_session.client_up

    @property
    def _zb_server_up(self) -> bool:
        return self._zb_current_session.server_up

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Routines only availabe on Wine / Windows, currently stubbed in zugbruecke
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @staticmethod
    def DllCanUnloadNow():  # EXPORT
        pass  # TODO stub - required for COM

    @staticmethod
    def DllGetClassObject(rclsid, riid, ppv):  # EXPORT
        pass  # TODO stub - required for COM

    class HRESULT:  # EXPORT
        pass  # TODO stub - special form of c_long, will require changes to argument parser

    @staticmethod
    def _check_HRESULT(result):  # EXPORT
        pass  # TODO stub - method for HRESULT, checks error bit, raises error if true. Needs reimplementation.

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Wrapper around DLL / shared object interface classes
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Wrapper for CDLL class
    def CDLL(
        self,
        name,
        mode=DEFAULT_MODE,
        handle=None,  # TODO ignored, see #54
        use_errno=False,
        use_last_error=False,
    ):

        return self._zb_current_session.load_library(
            name=name,
            convention="cdll",
            mode=mode,
            use_errno=use_errno,
            use_last_error=use_last_error,
        )

    # Wrapper for WinDLL class
    def WinDLL(
        self,
        name,
        mode=DEFAULT_MODE,
        handle=None,  # TODO ignored, see #54
        use_errno=False,
        use_last_error=False,
    ):

        return self._zb_current_session.load_library(
            name=name,
            convention="windll",
            mode=mode,
            use_errno=use_errno,
            use_last_error=use_last_error,
        )

    # Wrapper for OleDLL class
    def OleDLL(
        self,
        name,
        mode=DEFAULT_MODE,
        handle=None,  # TODO ignored, see #54
        use_errno=False,
        use_last_error=False,
    ):

        return self._zb_current_session.load_library(
            name=name,
            convention="oledll",
            mode=mode,
            use_errno=use_errno,
            use_last_error=use_last_error,
        )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# more static components from ctypes
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

_ctypes_veryprivate = ["__version__"]

_ctypes_private = [
    "_CFuncPtr",
    "_FUNCFLAG_PYTHONAPI",
    "_FUNCFLAG_USE_ERRNO",
    "_FUNCFLAG_USE_LASTERROR",
    "_Pointer",
    "_SimpleCData",
    "_calcsize",
    "_cast",
    "_cast_addr",
    "_check_size",
    "_ctypes_version",
    "_dlopen",  # behaviour depends on platform
    "_endian",
    "_memmove_addr",
    "_memset_addr",
    "_pointer_type_cache",
    "_reset_cache",
    "_string_at",
    "_string_at_addr",
    "_wstring_at",
    "_wstring_at_addr",
]

_ctypes_public = [
    "ARRAY",  # Python 3.6: Deprecated XXX
    "ArgumentError",
    "Array",
    "BigEndianStructure",
    "LittleEndianStructure",
    "POINTER",
    "PYFUNCTYPE",
    "PyDLL",
    "RTLD_GLOBAL",
    "RTLD_LOCAL",
    "SetPointerType",  # Python 3.6: Deprecated XXX
    "Structure",
    "Union",
    "addressof",
    "alignment",
    "byref",
    "c_bool",
    "c_buffer",
    "c_byte",
    "c_char",
    "c_char_p",
    "c_double",
    "c_float",
    "c_int",
    "c_int16",
    "c_int32",
    "c_int64",
    "c_int8",
    "c_long",
    "c_longdouble",
    "c_longlong",
    "c_short",
    "c_size_t",
    "c_ssize_t",
    "c_ubyte",
    "c_uint",
    "c_uint16",
    "c_uint32",
    "c_uint64",
    "c_uint8",
    "c_ulong",
    "c_ulonglong",
    "c_ushort",
    "c_void_p",
    "c_voidp",
    "c_wchar",
    "c_wchar_p",
    "cast",
    "create_string_buffer",
    "create_unicode_buffer",
    "get_errno",
    "memmove",
    "memset",
    "pointer",
    "py_object",
    "pydll",
    "pythonapi",
    "resize",
    "set_errno",
    "sizeof",
    "string_at",
    "wstring_at",
]

for _ctypes_item in _ctypes_veryprivate + _ctypes_private + _ctypes_public:
    _ctypes_attr = getattr(_ctypes, _ctypes_item)
    if hasattr(_ctypes_attr, "__call__"):
        _ctypes_attr = staticmethod(_ctypes_attr)
    setattr(CtypesSession, _ctypes_item, _ctypes_attr)
