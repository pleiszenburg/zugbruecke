# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/wineserver.py: Class(es) for managing wineserver

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import fcntl
import os
import signal
import socket
import subprocess
import struct
import sys
import time


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
		self.log.out('[wine] STARTING ...')

		# Session is up
		self.up = True

		# Set environment variables
		self.__set_wine_env__()

		# Create WINEPREFIX if it does not exist yet
		self.__create_wine_prefix__()

		# Start wine server
		self.__start__()

		# Log status
		self.log.out('[wine] STARTED.')


	# session destructor
	def terminate(self):

		if self.up:

			# Log status
			self.log.out('[wine] TERMINATING ...')

			# Stop wine server
			self.__stop__()

			# Log status
			self.log.out('[wine] TERMINATED.')

			# Session is down
			self.up = False


	def __create_wine_prefix__(self):

		# Log status
		self.log.out('[wine] Checking for WINEPREFIX directory "%s"...' % self.dir_wineprefix)

		# Does it exist?
		if not os.path.exists(self.dir_wineprefix):

			# Log status
			self.log.out('[wine] ... does not exists, creating ...')

			# Start wine server into prepared environment
			proc_winecfg = subprocess.Popen(
				['wineboot', '-i'],
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
			self.log.out('[wine] ... done.')

		else:

			# Log status
			self.log.out('[wine] ... exists.')


	def __set_wine_env__(self):

		# Change the environment for Wine: Architecture
		os.environ['WINEARCH'] = self.p['arch']

		# Log status
		self.log.out('[wine] Set WINEARCH env. variable: "%s"' % self.p['arch'])

		# Change the environment for Wine: Wine prefix / profile directory
		self.dir_wineprefix = os.path.join(
			self.p['dir'], self.p['arch'] + '-wine'
			)
		os.environ['WINEPREFIX'] = self.dir_wineprefix

		# Log status
		self.log.out('[wine] Set WINEPREFIX env. variable: "%s"' % self.dir_wineprefix)


	def __start__(self):

		# Status log
		self.log.out('[wine] Launching wineserver ...')

		# Start wine server into prepared environment
		self.proc_wineserver = subprocess.Popen(
			['wineserver', '-f', '-p'], # run persistent in foreground
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = False
			)

		# Status log
		self.log.out('[wine] ... started with PID %d.' % self.proc_wineserver.pid)

		# Get info on WINEPREFIX folder
		info_wineprefix = os.stat(self.dir_wineprefix)

		# Get path of wineserver socket file
		self.server_path = os.path.join(
			'/tmp', # Folder is hard-coded into Wine
			'.wine-%d' % os.getuid(),
			'server-%x-%x' % (info_wineprefix.st_dev, info_wineprefix.st_ino)
			)

		# [CHECK #1] Wait for lock ...
		self.__wait_for_lock__()

		# [CHECK #2] Wait for socket ...
		# self.__wait_for_socket__()

		# [CHECK #3] Testing the server by converting a path
		dir_cwd_wine = self.translate_path_unix2win(os.getcwd())


	def __get_lock_pid__(self, file_descriptor):
		"""
		Return process ID responsible for locking a file descriptor.
		Courtesy of: Sebastian Lackner <sebastian@fds-team.de>
		"""

		l_type = fcntl.F_WRLCK
		l_whence = 0 # SEEK_SET
		l_start = 0
		l_len = 0
		l_pid = 0

		lock = struct.pack('hhlli', l_type, l_whence, l_start, l_len, l_pid)
		lock = fcntl.fcntl(file_descriptor, fcntl.F_GETLK, lock)
		l_type, l_whence, l_start, l_len, l_pid = struct.unpack('hhlli', lock)

		if l_type != fcntl.F_UNLCK:
			return l_pid
		else:
			return None


	def __wait_for_lock__(self):

		# Get full path of socket
		lock_path = os.path.join(self.server_path, 'lock')

		# Status log
		self.log.out('[wine] Expecting wineserver lock at %s ...' % lock_path)

		# Status variable
		got_lock_pid = False
		# Time-step
		wait_for_seconds = 0.01
		# Timeout
		timeout_after_seconds = 30.0
		# Already waited for ...
		started_waiting_at = time.time()
		# Connection trys
		tried_this_many_times = 0

		# Run loop until socket appears
		while True:

			# Does socket file exist?
			if os.path.exists(lock_path):

				# Count attempts
				tried_this_many_times += 1

				# Open lock file
				lock_file = open(lock_path, 'rb')
				# Can I retrieve a PID?
				lock_pid = self.__get_lock_pid__(lock_file)
				# Close lock file
				lock_file.close()

				# Check result
				if lock_pid is not None:
					got_lock_pid = True
					break

			# Break the loop after timeout
			if time.time() >= (started_waiting_at + timeout_after_seconds):
				break

			# Wait before trying again
			time.sleep(wait_for_seconds)

		# Evaluate the result
		if not got_lock_pid:

			self.log.out(
				'[wine] ... was not locked %d (after %0.2f seconds & %d attempts)! Quit.' % (
					timeout_after_seconds, tried_this_many_times
					)
				)
			sys.exit()

		else:

			# Log status
			self.log.out(
				'[wine] ... is locked by PID %d (after %0.2f seconds & %d attempts)!' % (
					lock_pid, time.time() - started_waiting_at, tried_this_many_times
					)
				)


	def __wait_for_socket__(self, test_connect = False):

		# Get full path of socket
		socket_path = os.path.join(self.server_path, 'socket')

		# Status log
		self.log.out('[wine] Expecting wineserver socket at %s ...' % socket_path)

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
		started_waiting_at = time.time()
		# Connection trys
		tried_this_many_times = 0

		# Run loop until socket appears
		while True:

			# Does socket file exist?
			if os.path.exists(socket_path):

				# Count attempts
				tried_this_many_times += 1

				# Socket file exists - should connection be attemted?
				if test_connect:

					# Can I connect to it?
					try:
						wineserver_client.connect(socket_path)
						got_connection = True
						break
					except:
						pass

				else:

					got_connection = True

			# Break the loop after timeout
			if time.time() >= (started_waiting_at + timeout_after_seconds):
				break

			# Wait before trying again
			time.sleep(wait_for_seconds)

		# Evaluate the result
		if not got_connection:

			self.log.out(
				'[wine] ... did not appear (after %0.2f seconds & %d attempts)! Quit.' % (
					timeout_after_seconds, tried_this_many_times
					)
				)
			sys.exit()

		else:

			if test_connect:

				# If it worked, disconnect
				wineserver_client.close()

			# Log status
			self.log.out(
				'[wine] ... appeared (after %0.2f seconds & %d attempts)!' % (
					time.time() - started_waiting_at, tried_this_many_times
					)
				)


	def __stop__(self):

		# Killing the server requires two signals as specified in the man page
		os.kill(self.proc_wineserver.pid, signal.SIGINT)
		os.kill(self.proc_wineserver.pid, signal.SIGKILL)
		# os.killpg(os.getpgid(self.proc_wineserver.pid), signal.SIGINT)
		# os.killpg(os.getpgid(self.proc_wineserver.pid), signal.SIGKILL)


	def translate_path_unix2win(self, path):
		"""
		*WORKAROUND*
		Hacked version of "translate_path_unix2win", rerunning the command for
		until it succeeds (or ``max_attempts`` is reached).
		"""

		# Pass stderr into log
		self.log.out('[wine] Translating path ...')
		self.log.out('[wine] ... input: "%s" ...' % path)

		# Count attempts
		tried_this_many_times = 0
		# Specify max attempts
		max_attempts = 25 # on really slow machines even this fails at the moment BUG
		# Timeout after seconds per attempt
		time_out_after_seconds = 0.1
		# Status variable
		path_converted = False

		# Really bad HACK: Loop until max attempts are reached or path is converted
		while tried_this_many_times < max_attempts:

			# Count attempts
			tried_this_many_times += 1

			# Log status
			self.log.out('[wine] ... attempt %d to call winepath ...' % tried_this_many_times)

			# Start winepath for tanslating path, catch output from all pipes
			winepath_p = subprocess.Popen(
				['winepath', '-w', path],
				stdout = subprocess.PIPE,
				stderr = subprocess.PIPE
				)

			# Log status
			self.log.out('[wine] ... process started with PID %d ...' % winepath_p.pid)

			# Get stdout and stderr with timeout
			try:
				wine_out, wine_err = winepath_p.communicate(timeout = time_out_after_seconds)
			except subprocess.TimeoutExpired:
				self.log.out('[wine] ... timed out, killing process ...')
				winepath_p.kill()
				wine_out, wine_err = b'', b''

			# Change encoding
			wine_out = wine_out.decode(encoding = 'UTF-8').strip()

			# Pass stderr into log
			self.log.err(wine_err.decode(encoding = 'UTF-8'))

			# Check result
			if wine_out != '':

				# Update status: It worked.
				path_converted = True

				# Break the loop
				break

		# Log status
		self.log.out('[wine] ... output: "%s".' % wine_out)

		# Catch errors
		if wine_out == '' or not path_converted:

			# Log status
			self.log.out('[wine] ... failed!')

			raise # TODO error

		# Return translated path
		return wine_out


	def __translate_path_unix2win__(self, path):
		"""
		Original, currently unused version of "translate_path_unix2win". Not failsafe.
		"""

		# Pass stderr into log
		self.log.out('[wine] Translate path input: "%s"' % path)

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
		self.log.out('[wine] Translate path output: "%s"' % wine_out)

		# Catch errors
		if wine_out == '':
			raise # TODO error

		# Return translated path
		return wine_out
