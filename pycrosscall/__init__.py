
import atexit as _atexit
import random as _random


def _get_randhashstr(dig):

	return (('%0' + str(dig) + 'x') % _random.randrange(16**dig))


def _generate_session_id():

	return _get_randhashstr(8)


def _unload_module():

	print('LINUX (%s): pycrosscall unloaded' % session_id)


session_id = _generate_session_id()
print('LINUX (%s): pycrosscall imported' % session_id)

_atexit.register(_unload_module)
