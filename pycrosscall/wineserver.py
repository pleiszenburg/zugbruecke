# -*- coding: utf-8 -*-

"""

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	pycrosscall/wine.py: Class(es) for managing wineserver

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

import os
import signal
import socket
import subprocess
import sys
import tempfile
import time

from .xmlrpc import xmlrpc_client


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wineserver_session_class:


	# session init
	def __init__(self, session_id, parameter, session_log):

		# Set ID, parameters and pointer to log
		self.id = session_id
		self.p = parameter
		self.log = session_log

		# Log status
		self.log.out('[wine session] STARTING ...')

		# Session is up
		self.up = True

		# Set environment variables
		self.__set_wine_env__()

		# Create WINEPREFIX if it does not exist yet
		self.__create_wine_prefix__()

		# Start wine server
		self.__wine_server_start__()

		# Log status
		self.log.out('[wine session] STARTED.')


	# session destructor
	def terminate(self):

		if self.up:

			# Log status
			self.log.out('[wine session] TERMINATING ...')

			# Stop wine server
			self.__wine_server_stop__()

			# Log status
			self.log.out('[wine session] TERMINATED.')

			# Session is down
			self.up = False


	def __create_wine_prefix__(self):

		# Log status
		self.log.out('[wine session] Checking for WINEPREFIX directory "%s"...' % self.dir_wineprefix)

		# Does it exist?
		if not os.path.exists(self.dir_wineprefix):

			# Log status
			self.log.out('[wine session] ... does not exists, creating ...')

			# Start wine server into prepared environment
			proc_winecfg = subprocess.Popen(
				['winecfg'],
				stdin = subprocess.PIPE,
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE,
				shell = False
				)

			# Get feedback
			cfg_out, cfg_err = proc_winecfg.communicate()

			# Log feedback
			self.log.out(cfg_out.decode(encoding = 'UTF-8'))
			self.log.err(cfg_err.decode(encoding = 'UTF-8'))

			# Log status
			self.log.out('[wine session] ... done.')

		else:

			# Log status
			self.log.out('[wine session] ... exists.')


	def __set_wine_env__(self):

		# Change the environment for Wine: Architecture
		os.environ['WINEARCH'] = self.p['arch']

		# Log status
		self.log.out('[wine session] Set WINEARCH env. variable: "%s"' % self.p['arch'])

		# Change the environment for Wine: Wine prefix / profile directory
		self.dir_wineprefix = os.path.join(
			self.p['dir'], self.p['arch'] + '-wine'
			)
		os.environ['WINEPREFIX'] = self.dir_wineprefix

		# Log status
		self.log.out('[wine session] Set WINEPREFIX env. variable: "%s"' % self.dir_wineprefix)


	def __wine_server_start__(self):

		# Status log
		self.log.out('[wine session] Launching wineserver ...')

		# Start wine server into prepared environment
		self.proc_wineserver = subprocess.Popen(
			['wineserver', '-f', '-p'], # run persistent in foreground
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = False
			)

		# Status log
		self.log.out('[wine session] ... started with PID %d ...' % self.proc_wineserver.pid)

		# Get info on WINEPREFIX folder
		info_wineprefix = os.stat(self.dir_wineprefix)

		# Get path of wineserver socket file
		socket_path = os.path.join(
			tempfile.gettempdir(),
			'.wine-%d' % os.getuid(),
			'server-%x-%x' % (info_wineprefix.st_dev, info_wineprefix.st_ino),
			'socket'
			)

		# Status log
		self.log.out('[wine session] ... expecting socket at %s ...' % socket_path)

		# Create socket client
		wineserver_client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		# Set a timeout
		wineserver_client.settimeout(1.0) # seconds
		# Status variable
		got_connection = False
		# Time-step
		wait_for_seconds = 0.01
		# Timeout
		timeout_after_seconds = 30.0
		# Already waited for ...
		waited_for_seconds = 0.0
		# Connection trys
		tried_this_many_times = 0

		# Run loop until socket appears
		while True:

			# Does socket file exist?
			if os.path.exists(socket_path):

				# Count attempts
				tried_this_many_times += 1

				# Can I connect to it?
				try:
					wineserver_client.connect(socket_path)
					got_connection = True
					break
				except:
					pass

			# Keep track of time
			waited_for_seconds += wait_for_seconds

			# Break to loop after timeout
			if waited_for_seconds >= timeout_after_seconds:
				break

			# Wait before trying again
			time.sleep(wait_for_seconds)

		# Evaluate the result
		if not got_connection:

			self.log.out(
				'[wine session] ... did not appear (after %0.2f seconds & %d attempts)! Quit.' % (timeout_after_seconds, tried_this_many_times)
				)
			sys.exit()

		else:

			# If it worked, disconnect
			wineserver_client.close()

			# Log status
			self.log.out(
				'[wine session] ... appeared (after %0.2f seconds & %d attempts)!' % (waited_for_seconds, tried_this_many_times)
				)


	def __wine_server_stop__(self):

		# Killing the server requires two signals as specified in the man page
		os.kill(self.proc_wineserver.pid, signal.SIGINT)
		os.kill(self.proc_wineserver.pid, signal.SIGKILL)
		# os.killpg(os.getpgid(self.proc_wineserver.pid), signal.SIGINT)
		# os.killpg(os.getpgid(self.proc_wineserver.pid), signal.SIGKILL)


	def translate_path_unix2win(self, path):

		# Pass stderr into log
		self.log.out('[wine session] Translate path input: "%s"' % path)

		# Start winepath for tanslating path, catch output from all pipes
		winepath_p = subprocess.Popen(
			['winepath', '-w', path],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
			)

		# Get stdout and stderr
		wine_out, wine_err = winepath_p.communicate()

		# Change encoding
		wine_out = wine_out.decode(encoding = 'UTF-8').strip()

		# Pass stderr into log
		self.log.err(wine_err.decode(encoding = 'UTF-8'))

		# Pass stderr into log
		self.log.out('[wine session] Translate path output: "%s"' % wine_out)

		# Catch errors
		if wine_out == '':
			raise # TODO error

		# Return translated path
		return wine_out
