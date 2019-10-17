
import os
from sys import platform

from .const import ARCHS
from .names import get_dll_path

if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
elif platform.startswith('win'):
	import ctypes
else:
	raise SystemError('unsopported platform')

def get_dll_handle(arch, convention, test_fn):
	"get handle to dll for given arch and convention"

	return getattr(ctypes, convention).LoadLibrary(
		get_dll_path(arch, convention, test_fn)
		)

def get_dll_handles(test_path):
	"get handles to one test's dlls for all archs and conventions"

	test_fn = os.path.basename(test_path)

	return (get_dll_handle(arch, 'windll', test_fn) for arch in ARCHS)
