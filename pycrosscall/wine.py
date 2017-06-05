# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import signal
import subprocess

from .lib import get_location_of_file


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wine_session_class:


	def __init__(self, session_id, parameter, session_log):

		self.id = session_id
		self.p = parameter
		self.log = session_log

		self.log.out('wine session starting ...')

		# Get location of this script file
		self.location = get_location_of_file(__file__)

		self.__server_start__()

		self.log.out('wine session started')


	def terminate(self):

		self.__server_stop__()

		self.log.out('wine session terminated')


	def __set_env__(self):

		# Change the environment for Wine: Architecture
		os.environ['WINEARCH'] = self.p['arch']

		# Change the environment for Wine: Wine prefix / profile directory
		os.environ['WINEPREFIX'] = os.path.join(self.location, self.p['arch'] + '-wine')


	def __server_start__(self):

		# Set environment variables
		self.__set_env__()

		# Python interpreter's directory seen from this script
		pydir_unix = os.path.join(self.location, self.p['arch'] + '-python' + self.p['version'])

		# Translate Python interpreter's Unix path into Wine path
		pydir_win = self.translate_path_unix2win(pydir_unix)

		# Prepare Wine-Python server command with session id
		py_cmd = pydir_win + '\\python.exe win_server.py ' + self.id

		# Identify wine command for 32 or 64 bit
		if self.p['arch'] == 'win32':
			wine_cmd = 'wine'
		else: # win64
			wine_cmd = 'wine64'

		# Launch server
		self.wine_p = subprocess.Popen(
			'echo "%s" | %s cmd &' % (py_cmd, wine_cmd),
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = True,
			preexec_fn = os.setsid
			)


	def __server_stop__(self):

		os.killpg(os.getpgid(self.wine_p.pid), signal.SIGTERM)


	def translate_path_unix2win(self, path):

		# Start winepath for tanslating path, catch output from all pipes
		winepath_p = subprocess.Popen(
			['winepath', '-w', path],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
			)
		# Get stdout and stderr
		wine_out, wine_err = winepath_p.communicate()

		# Pass stderr into log
		self.log.err(wine_err.decode(encoding = 'UTF-8'))

		# Return translated path
		return wine_out.decode(encoding = 'UTF-8').strip()
