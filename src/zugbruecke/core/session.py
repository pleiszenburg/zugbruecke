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

from types import TracebackType
from typing import Any, Callable, Optional, Type, Union


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
# UTILS-DROP-IN-REPLACEMENT CLASS, BOUND TO SESSION
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class _util:
    """
    Session-bound wrapper for ``ctypes.util``. Immutable.
    """

    def __init__(self, session_id: str, find_library: Callable, find_msvcrt: Callable):

        self._id = session_id
        self._find_library = find_library
        self._find_msvcrt = find_msvcrt

    def __repr__(self) -> str:

        return f'<CtypesSession.util id={self._id:s}>'

    def find_library(self, *args: Any, **kwargs: Any) -> Any:

        return self._find_library(*args, **kwargs)

    def find_msvcrt(self, *args: Any, **kwargs: Any) -> Any:

        return self._find_msvcrt(*args, **kwargs)

    @property
    def zb_id(self) -> str:
        "id of bound CtypesSession instance"

        return self._id


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SESSION CTYPES-DROP-IN-REPLACEMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class CtypesSession(CtypesSessionABC):
    """
    Represents one "ctypes session", i.e. one Wine Python process, related infrastructure
    and its independent configuration. Mutliple sessions can run simultaneously. Mutable.

    args:
        config : Session's configuration. If not provided, settings will be read from configuration files and environment variables, see :class:`zugbruecke.Config`.
    """

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

        self._util = _util(
            session_id=self._zb_current_session.id,
            find_library=self._zb_current_session.find_library,
            find_msvcrt=self._zb_current_session.find_msvcrt,
        )

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

    def __repr__(self) -> str:
        """
        String representation for interactive use
        """

        return '<CtypesSession id={ID:s} arch={ARCH:s} build={BUILD:s} client_up={CLIENT_UP:s} client_up={SERVER_UP:s}>'.format(
            ID = self._zb_current_session.id,
            ARCH = self._zb_current_session.config['arch'],
            BUILD = str(self._zb_current_session.config['pythonversion']),
            CLIENT_UP = str(self._zb_current_session.client_up),
            SERVER_UP = str(self._zb_current_session.server_up),
        )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # context
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def __enter__(self) -> CtypesSessionABC:
        """
        Context manager entry point.
        """

        return self

    def __exit__(
        self,
        exc_type: Union[Type, None],
        exc_value: Union[Exception, None],
        traceback: Union[TracebackType, None],
    ):
        """
        Context manager exit point.

        Args:
            exc_type : Type of exception
            exc_value : Actual exception object
            traceback : Related traceback object
        """

        self._zb_terminate()

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Allow readonly access to session states
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def util(self) -> _util:
        """
        Regular ``ctypes`` has a submodule named ``ctypes.util``. In ``zugbruecke``, this functionality is bound to a session.
        On a per-session level, it is exposed via this attribute.

        returns:
            Drop-in replacement for ``ctypes.util``
        """

        return self._util

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Allow readonly access to session states
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def _zb_id(self) -> str:
        """
        Session ID string
        """

        return self._zb_current_session.id

    @property
    def _zb_client_up(self) -> bool:
        """
        Client status
        """

        return self._zb_current_session.client_up

    @property
    def _zb_server_up(self) -> bool:
        """
        Server status
        """

        return self._zb_current_session.server_up

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Routines only availabe on Wine / Windows, currently stubbed in zugbruecke
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @staticmethod
    def DllCanUnloadNow():  # EXPORT
        """
        Stub, not implemented. Required for COM.
        """

        raise NotImplementedError()

    @staticmethod
    def DllGetClassObject(rclsid, riid, ppv):  # EXPORT
        """
        Stub, not implemented. Required for COM.
        """

        raise NotImplementedError()

    class HRESULT:  # EXPORT
        """
        Stub, not implemented. Required for COM. Special form of ``ctypes.c_long`` (32 bit).
        """

        def __init__(self, *args: Any, **kwargs: Any):

            raise NotImplementedError() # NOTE will require changes to argument parser

    @staticmethod
    def _check_HRESULT(result):  # EXPORT
        """
        Stub, not implemented. Required for COM. Method for HRESULT, checks error bit, raises error if true.
        """

        raise NotImplementedError() # NOTE needs reimplementation

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Wrapper around DLL / shared object interface classes
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def CDLL(
        self,
        name: str,
        mode: int = DEFAULT_MODE,
        handle: Any = None,  # TODO ignored, see #54
        use_errno: bool = False,
        use_last_error: bool = False,
        winmode: Optional[int] = None,
    ):
        """
        Drop-in replacement for ``ctypes.CDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        return self._zb_current_session.load_library(
            name=name,
            convention="cdll",
            mode=mode,
            use_errno=use_errno,
            use_last_error=use_last_error,
        )

    def WinDLL(
        self,
        name: str,
        mode: int = DEFAULT_MODE,
        handle: Any = None,  # TODO ignored, see #54
        use_errno: bool = False,
        use_last_error: bool = False,
        winmode: Optional[int] = None,
    ):
        """
        Drop-in replacement for ``ctypes.WinDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        return self._zb_current_session.load_library(
            name=name,
            convention="windll",
            mode=mode,
            use_errno=use_errno,
            use_last_error=use_last_error,
        )

    def OleDLL(
        self,
        name: str,
        mode: int = DEFAULT_MODE,
        handle: Any = None,  # TODO ignored, see #54
        use_errno: bool = False,
        use_last_error: bool = False,
        winmode: Optional[int] = None,
    ):
        """
        Drop-in replacement for ``ctypes.CDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        return self._zb_current_session.load_library(
            name=name,
            convention="oledll",
            mode=mode,
            use_errno=use_errno,
            use_last_error=use_last_error,
        )

    def PyDLL(
        self,
        name: str,
        mode: int = DEFAULT_MODE,
        handle: Any = None,  # TODO ignored, see #54
        use_errno: bool = False,
        use_last_error: bool = False,
        winmode: Optional[int] = None,
    ):
        """
        Stub, not implemented. Drop-in replacement for ``ctypes.PyDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        raise NotImplementedError()

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
