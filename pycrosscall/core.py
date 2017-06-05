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

		# Fill empty parameters with default values
		self.__fill_parameter__(parameter)

		# Generate unique session id
		self.id = generate_session_id()

		# Start session logging
		self.log = log_class(self.id, self.p)

		# TODO if debug
		self.log.out('pycrosscall import ...')

		# Initialize Wine session
		self.wine_session = wine_session_class(self.id, self.p, self.log)

		# Demo call into Wine
		test_path_unix = os.path.split(os.path.realpath(__file__))[0]
		test_path_win = self.wine_session.translate_path_unix2win(test_path_unix)
		self.log.out(test_path_unix)
		self.log.out(test_path_win)

		# Register session destructur
		atexit.register(self.terminate)

		# TODO if debug
		self.log.out('pycrosscall imported')


	def __fill_parameter__(self, parameter):

		self.p = parameter

		if 'stdout' not in self.p.keys():
			self.p['stdout'] = True

		if 'stderr' not in self.p.keys():
			self.p['stderr'] = True



	def terminate(self):

		self.wine_session.terminate()
		self.log.out('pycrosscall unloaded')
