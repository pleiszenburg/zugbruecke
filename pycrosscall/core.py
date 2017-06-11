# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/core.py: Core classes for managing pycrosscall sessions

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/s-m-e/pycrosscall/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import atexit
import os
from pprint import pprint as pp
import signal

from .config import get_module_config
from .wine import wine_session_class
from .log import log_class
from .dll import dll_session_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PYCROSSCALL SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class session_class():


	def __init__(self, parameter = {}):

		# Fill empty parameters with default values
		self.p = get_module_config(parameter)

		# Get and set session id
		self.id = self.p['id']

		# Start session logging
		self.log = log_class(self.id, self.p)

		# Log status
		self.log.out('pycrosscall import (Wine-Python %s %s) ...' % (self.p['version'], self.p['arch']))

		# Store current working directory
		self.dir_cwd = os.getcwd()

		# Initialize Wine session
		self.wine_session = wine_session_class(self.id, self.p, self.log)

		# Set up a dict for loaded dlls
		self.dll_dict = {}

		# Mark session as up
		self.up = True

		# Register session destructur
		atexit.register(self.terminate)
		signal.signal(signal.SIGINT, self.terminate)
		signal.signal(signal.SIGTERM, self.terminate)

		# Log status
		self.log.out('pycrosscall imported')


	def LoadLibrary(self, dll_name, dll_type = 'windll'):

		# Get full path of dll
		full_path_dll = os.path.join(self.dir_cwd, dll_name)

		# Check if dll file exists
		if not os.path.isfile(full_path_dll):

			raise # TODO

		# Simplyfy full path
		full_path_dll = os.path.abspath(full_path_dll)

		# Log status
		self.log.out('Accessing dll "%s" - exists.' % full_path_dll)

		# Check whether dll has yet not been touched
		if full_path_dll not in self.dll_dict.keys():

			# Fire up new dll object
			self.dll_dict[full_path_dll] = dll_session_class(
				full_path_dll, dll_name, dll_type, self
				)

		# Return reference on existing dll object
		return self.dll_dict[full_path_dll]


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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINDLL CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class windll_class(): # Mimic ctypes.windll


	def __init__(self):

		# Session not yet up
		self.up = False


	def start_session(self, parameter = {}):

		# Session not yet up?
		if not self.up:

			# Fire up a new session
			self.__session__ = session_class(parameter)

			# Mark session as up
			self.up = True


	def LoadLibrary(self, name):

		# Session not yet up?
		if not self.up:

			# Fire up session
			self.start_session()

		# Return a DLL instance object from within the session
		return self.__session__.LoadLibrary(dll_name = name, dll_type = 'windll')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# STAND-ALONE PYTHON INTERPRETER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class python_interpreter():


	def __init__(self, cmd_line_args):

		cfg = get_module_config()
		print(cfg)


	def run(self):

		pass
