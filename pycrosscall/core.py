# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import atexit
import os
import signal

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
		self.log.out('pycrosscall import (Wine-Python %s %s) ...' % (self.p['version'], self.p['arch']))

		# Initialize Wine session
		self.wine_session = wine_session_class(self.id, self.p, self.log)

		# Mark session as up
		self.up = True

		# Register session destructur
		atexit.register(self.terminate)
		signal.signal(signal.SIGINT, self.terminate)
		signal.signal(signal.SIGTERM, self.terminate)

		# Log status
		self.log.out('pycrosscall imported')


	def terminate(self):

		# Run only if session is still up
		if self.up:

			# Log status
			self.log.out('pycrosscall unloading ...')

			# Destruct wine session, quit wine processes
			self.wine_session.terminate()

			# Log status
			self.log.out('pycrosscall unloaded')

			# Terminate log
			self.log.terminate()

			# Session down
			self.up = False


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

		# Write log messages into file
		if 'logwrite' not in self.p.keys():
			self.p['logwrite'] = False

		# Port for xmlrpc server on Unix
		self.p['port_unix'] = 8001

		# Port for xmlrpc server on Wine
		self.p['port_wine'] = 8000

		# Open server for collected logs from clients
		self.p['log_server'] = True

		# Send log messages to remove sever
		self.p['remote_log'] = False

		# Define Wine & Wine-Python architecture
		if 'arch' not in self.p.keys():
			self.p['arch'] = 'win32'

		# Define Wine-Python version
		if 'version' not in self.p.keys():
			self.p['version'] = '3.5.3'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PATCHED CTYPES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class windll_class():


	def __init__(self):

		self.session = session_class()


	def LoadLibrary(self, name):

		print('Huh: ' + name)
