# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/session.py: A user-facing ctypes-drop-in-replacement session

    Required to run on platform / side: [UNIX]

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

from .abc import CtypesSessionABC
from .session_client import SessionClient
from .config import Config
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
        kwargs : An arbitrary number of keyword arguments matching valid :ref:`configuration parameters <configparameter>`
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

    def __init__(self, **kwargs: Any):

        # Start new zugbruecke session
        self._current_session = SessionClient(config=Config(**kwargs))

        # Routines from ctypes.util
        self._util = _util(
            session_id=self._current_session.id,
            find_library=self._current_session.find_library,
            find_msvcrt=self._current_session.find_msvcrt,
        )

        # Library loader objects
        self._cdll = LibraryLoader(self.CDLL)
        self._windll = LibraryLoader(self.WinDLL)
        self._oledll = LibraryLoader(self.OleDLL)
        self._pydll = LibraryLoader(self.PyDLL)

        # Used as cache by CFUNCTYPE and WINFUNCTYPE
        self._c_functype_cache = self._current_session.data.cache.by_conv(_FUNCFLAG_CDECL)
        self._win_functype_cache = self._current_session.data.cache.by_conv(_FUNCFLAG_STDCALL)


    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # repr
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def __repr__(self) -> str:
        """
        ``zugbruecke`` session string representation for interactive use
        """

        return '<CtypesSession id={ID:s} arch={ARCH:s} build={BUILD:s} client_up={CLIENT_UP:s} client_up={SERVER_UP:s}>'.format(
            ID = self._current_session.id,
            ARCH = self._current_session.config['arch'],
            BUILD = str(self._current_session.config['pythonversion']),
            CLIENT_UP = str(self._current_session.client_up),
            SERVER_UP = str(self._current_session.server_up),
        )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # context
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def __enter__(self) -> CtypesSessionABC:
        """
        Context manager entry point for ``zugbruecke`` session.
        """

        return self

    def __exit__(
        self,
        exc_type: Union[Type, None],
        exc_value: Union[Exception, None],
        traceback: Union[TracebackType, None],
    ):
        """
        Context manager exit point for ``zugbruecke`` session.

        Args:
            exc_type : Type of exception
            exc_value : Actual exception object
            traceback : Related traceback object
        """

        self.zb_terminate()

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Allow readonly access to session states
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def util(self) -> _util:
        """
        Regular ``ctypes`` has a submodule named ``ctypes.util``. In ``zugbruecke``, this functionality is bound to a session.
        On a per-session level, it is exposed via this attribute.

        returns:
            Drop-in replacement for ``ctypes.util``. Offers ``zugbruecke`` wrappers for ``find_library`` and ``find_msvcrt``.
        """

        return self._util

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Allow readonly access to session states
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def zb_get_parameter(self, key: str) -> Any:
        """
        Reads configuration parameter of this session

        args:
            key : Name of configuration parameter
        returns:
            Value for configuration parameter
        """

        return self._current_session.get_parameter(key = key)

    def zb_set_parameter(self, key: str, value: Any):
        """
        Changes configuration parameter of this session (both on Unix/client and Wine/server side)

        args:
            key : Name of configuration parameter
            value : New value for configuration parameter
        """

        self._current_session.set_parameter(key = key, value = value)

    def zb_terminate(self):
        """
        This method can be used to manually terminate a session. It will quit the *Windows* *Python* interpreter running in the background. Once terminated, a session can not be re-started. Any handles on DLLs and their routines derived from this session will become useless.
        """

        self._current_session.terminate()

    @property
    def zb_id(self) -> str:
        """
        Session ID string
        """

        return self._current_session.id

    @property
    def zb_client_up(self) -> bool:
        """
        Client status
        """

        return self._current_session.client_up

    @property
    def zb_server_up(self) -> bool:
        """
        Server status
        """

        return self._current_session.server_up

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Windows vs. Unix paths
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def zb_path_unix_to_wine(self, path: str) -> str:
        """
        Path conversion, Unix to Windows/Wine.
        It uses *Wine*'s internal implementation for path conversions. It does not check, whether the path actually exists or not.

        args:
            path : Unix path. Path can be absolute or relative.
        returns:
            Windows/Wine path
        """

        return self._current_session.path_unix_to_wine(path)

    def zb_path_wine_to_unix(self, path: str) -> str:
        """
        Path conversion, Windows/Wine to Unix.
        It uses *Wine*'s internal implementation for path conversions. It does not check, whether the path actually exists or not.

        args:
            path : Windows/Wine path. Path can be absolute or relative.
        returns:
            Unix path
        """

        return self._current_session.path_wine_to_unix(path)

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

        args:
            args : positional arguments
            kwargs : keyword arguments
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
    # Routines only availabe on Wine / Windows - accessed via server
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def FormatError(self, *args: Any, **kwargs: Any) -> Any:
        """
        ``zugbruecke`` wrapper for ``ctypes.FormatError``, untested.

        args:
            args : positional arguments
            kwargs : keyword arguments
        returns:
            A textual description of the error code code. If no error code is specified, the last error code is used by calling the Windows api function GetLastError.
        """

        return self._current_session.FormatError(*args, **kwargs)

    def get_last_error(self, *args: Any, **kwargs: Any) -> Any:
        """
        ``zugbruecke`` wrapper for ``ctypes.get_last_error``, untested.

        args:
            args : positional arguments
            kwargs : keyword arguments
        returns:
            The current value of the ctypes-private copy of the system ``LastError`` variable in the calling thread.
        """

        return self._current_session.get_last_error(*args, **kwargs)

    def GetLastError(self, *args: Any, **kwargs: Any) -> Any:
        """
        ``zugbruecke`` wrapper for ``ctypes.GetLastError``, untested.

        args:
            args : positional arguments
            kwargs : keyword arguments
        returns:
            The last error code set by Windows in the calling thread. This function calls the Windows ``GetLastError()`` function directly, it does not return the ctypes-private copy of the error code.
        """

        return self._current_session.GetLastError(*args, **kwargs)

    def set_last_error(self, *args: Any, **kwargs: Any) -> Any:
        """
        ``zugbruecke`` wrapper for ``ctypes.set_last_error``, untested.

        Set the current value of the ctypes-private copy of the system ``LastError`` variable in the calling thread to valueself.

        args:
            args : positional arguments
            kwargs : keyword arguments
        returns:
            The previous value.
        """

        return self._current_session.set_last_error(*args, **kwargs)

    def WinError(self, *args: Any, **kwargs: Any) -> Any:
        """
        ``zugbruecke`` wrapper for ``ctypes.WinError``, untested.

        This function is probably the worst-named thing in ctypes.

        args:
            args : positional arguments
            kwargs : keyword arguments
        returns:
            An instance of ``OSError``.
        """

        return self._current_session.WinError(*args, **kwargs)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # CFUNCTYPE & WINFUNCTYPE
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def CFUNCTYPE(self, restype: Any, *argtypes: Any, use_errno: bool = False, use_last_error: bool = False) -> Type:
        """
        ``zugbruecke`` drop-in replacement for ``ctypes.CFUNCTYPE``

        args:
            restype : ctypes type of return value
            argtypes : ctypes types of arguments
            use_errno : If true, the ctypes private copy of the system errno variable is exchanged with the real errno value before and after the call.
            use_last_error : Does the same for the Windows error code.
        """

        return self._current_session.CFUNCTYPE(restype, *argtypes, use_errno = use_errno, use_last_error = use_last_error)

    def WINFUNCTYPE(self, restype: Any, *argtypes: Any, use_errno: bool = False, use_last_error: bool = False) -> Type:
        """
        ``zugbruecke`` drop-in replacement for ``ctypes.WINFUNCTYPE``

        args:
            restype : ctypes type of return value
            argtypes : ctypes types of arguments
            use_errno : If true, the ctypes private copy of the system errno variable is exchanged with the real errno value before and after the call.
            use_last_error : Does the same for the Windows error code.
        """

        return self._current_session.WINFUNCTYPE(restype, *argtypes, use_errno = use_errno, use_last_error = use_last_error)

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
        ``zugbruecke`` drop-in replacement for ``ctypes.CDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        return self._current_session.load_library(
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
        ``zugbruecke`` drop-in replacement for ``ctypes.WinDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        return self._current_session.load_library(
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
        ``zugbruecke`` drop-in replacement for ``ctypes.CDLL``

        args:
            name : Pathname of the shared library (DLL file)
            mode : Ignored on Windows, therefore ignored by ``zugbruecke``
            handle : Ignored by ``zugbruecke``, see issue #54
            use_errno : Enables a ``ctypes`` mechanism that allows accessing the system errno error number in a safe way.
            use_last_error : Enables the same mechanism for the Windows error code which is managed by the ``GetLastError()`` and ``SetLastError()`` Windows API functions.
            winmode : Ignored by ``zugbruecke``. Used on Windows to specify how the library is loaded (since mode is ignored)
        """

        return self._current_session.load_library(
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
        Stub, not implemented. ``zugbruecke`` drop-in replacement for ``ctypes.PyDLL``

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
    # Library loader objects
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    @property
    def cdll(self) -> LibraryLoader:
        """
        ``zugbruecke`` drop-in replacement for ``LibraryLoader(CDLL)`` aka ``ctypes.cdll``
        """

        return self._cdll

    @property
    def windll(self) -> LibraryLoader:
        """
        ``zugbruecke`` drop-in replacement for ``LibraryLoader(WinDLL)`` aka ``ctypes.windll``
        """

        return self._windll

    @property
    def oledll(self) -> LibraryLoader:
        """
        ``zugbruecke`` drop-in replacement for ``LibraryLoader(OleDLL)`` aka ``ctypes.oledll``
        """

        return self._oledll

    @property
    def pydll(self) -> LibraryLoader:
        """
        ``zugbruecke`` drop-in replacement for ``LibraryLoader(PyDLL)`` aka ``ctypes.pydll``
        """

        return self._pydll


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
