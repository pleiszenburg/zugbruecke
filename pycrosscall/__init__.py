
import atexit as _atexit

def _unload_module():

	print('LINUX: pycrosscall unloaded')


print('LINUX: pycrosscall imported')

_atexit.register(_unload_module)
