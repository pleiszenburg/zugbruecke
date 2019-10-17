
from sys import platform

if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
elif platform.startswith('win'):
	import ctypes
else:
	raise SystemError('unsopported platform')
