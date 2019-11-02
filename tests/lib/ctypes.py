
import os
from sys import platform
from platform import architecture

from .const import ARCHS, CONVENTIONS
from .names import get_dll_path

ARCHITECTURE = architecture()[0][:2]

if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke
	CTYPES = {arch: zugbruecke.ctypes_session({'arch': arch}) for arch in ARCHS}
	PLATFORM = 'unix'
elif platform.startswith('win'):
	import ctypes
	CTYPES = {arch: ctypes for arch in ARCHS}
	PLATFORM = 'wine'
else:
	raise SystemError('unsopported platform')

def get_dll_handle(arch, convention, test_fn):
	"get handle to dll for given arch and convention"

	return getattr(CTYPES[arch], convention).LoadLibrary(
		get_dll_path(arch, convention, test_fn) # TODO this will parse setup.cfg on EVERY call
		)

def get_dll_handles(test_path):
	"get handles to one test's dlls for all archs and conventions"

	test_fn = os.path.basename(test_path)

	for convention in CONVENTIONS:
		for arch in ARCHS:
			if PLATFORM == 'unix' or arch[3:] == ARCHITECTURE:
				yield (CTYPES[arch], get_dll_handle(arch, convention, test_fn))
