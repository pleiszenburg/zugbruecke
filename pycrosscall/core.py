# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import atexit
import os

from .wine import wine_session_class
from .lib import generate_session_id
from .log import log_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PYCROSSCALL SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session():


	def __init__(self, parameter = {}):

		# Generate unique session id
		self.id = generate_session_id()

		# Start session logging
		self.log = log_class(self.id)

		# TODO if debug
		self.log.out('pycrosscall import ...')

		# Initialize Wine session
		self.wine_session = wine_session_class(self.id, self.log)

		# Demo call into Wine
		test_path_unix = os.path.split(os.path.realpath(__file__))[0]
		test_path_win, err = self.wine_session.translate_path_unix2win(test_path_unix)
		print(test_path_unix)
		print(test_path_win)
		print(len(err), err)

		# Register session destructur
		atexit.register(self.terminate)

		# TODO if debug
		self.log.out('pycrosscall imported')


	def terminate(self):

		self.wine_session.terminate()
		self.log.out('pycrosscall unloaded')
