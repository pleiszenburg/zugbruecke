
import atexit as _atexit
import random as _random
import os as _os

from .wine import wine_session_class as _wine_session_class


def _get_randhashstr(dig):

	return (('%0' + str(dig) + 'x') % _random.randrange(16**dig))


def _generate_session_id():

	return _get_randhashstr(8)


def _unload_module():

	print('UNIX (%s): pycrosscall unloaded' % session_id)


session_id = _generate_session_id()
print('UNIX (%s): pycrosscall imported' % session_id)

wine_session = _wine_session_class(session_id)
test_path_unix = _os.path.split(_os.path.realpath(__file__))[0]
test_path_win, err = wine_session._translate_path_unix2win(test_path_unix)
print(test_path_unix)
print(test_path_win)
print(len(err), err)

_atexit.register(_unload_module)
