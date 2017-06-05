# -*- coding: utf-8 -*-


import atexit as _atexit
import os as _os

from .wine import wine_session_class as _wine_session_class
from .lib import generate_session_id as _generate_session_id
from .log import log_class as _log_class


def _unload_module():

	wine_session.terminate()
	session_log.out('pycrosscall unloaded')

# Generate unique session id
session_id = _generate_session_id()

# Start session logging
session_log = _log_class(session_id)

session_log.out('pycrosscall import ...')


wine_session = _wine_session_class(session_id, session_log)
test_path_unix = _os.path.split(_os.path.realpath(__file__))[0]
test_path_win, err = wine_session.translate_path_unix2win(test_path_unix)
print(test_path_unix)
print(test_path_win)
print(len(err), err)

_atexit.register(_unload_module)

session_log.out('pycrosscall imported')
