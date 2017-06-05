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

class session_class():


	def __init__(self, parameter = {}):

		# Fill empty parameters with default values
		self.__fill_parameter__(parameter)

		# Start session logging
		self.log = log_class(self.id, self.p)

		# Log status
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

		# Log status
		self.log.out('pycrosscall imported')


	def __fill_parameter__(self, parameter):

		# Store parameter dict
		self.p = parameter

		# If no unique session id was passed, generate one
		if 'id' not in self.p.keys():
			self.id = generate_session_id()
		else:
			self.id = self.p['id']

		# Display messages from stdout
		if 'stdout' not in self.p.keys():
			self.p['stdout'] = True

		# Display messages from stderr
		if 'stderr' not in self.p.keys():
			self.p['stderr'] = True


	def terminate(self):

		# Destruct wine session, quit wine processes
		self.wine_session.terminate()

		# Log status
		self.log.out('pycrosscall unloaded')
