# -*- coding: utf-8 -*-


import atexit as _atexit
import os as _os

from .wine import wine_session_class as _wine_session_class
from .lib import generate_session_id as _generate_session_id


def _unload_module():

	wine_session.terminate()
	print('UNIX (%s): pycrosscall unloaded' % session_id)


session_id = _generate_session_id()
print('UNIX (%s): pycrosscall import ...' % session_id)

wine_session = _wine_session_class(session_id)
test_path_unix = _os.path.split(_os.path.realpath(__file__))[0]
test_path_win, err = wine_session.translate_path_unix2win(test_path_unix)
print(test_path_unix)
print(test_path_win)
print(len(err), err)

_atexit.register(_unload_module)

print('UNIX (%s): pycrosscall imported' % session_id)
