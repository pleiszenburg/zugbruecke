# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
from queue import Queue
import signal
import subprocess
import sys
from threading import Thread

import psutil

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
		# pydir_win = self.translate_path_unix2win(pydir_unix)

		# Translate server's Unix path into Wine path
		location_win = self.translate_path_unix2win(self.location)

		# Prepare Wine-Python server command with session id
		py_cmd = [
			os.path.join(pydir_unix, 'python.exe'),
			"%s\\wine_server.py" % location_win,
			self.id
			]

		# Identify wine command for 32 or 64 bit
		if self.p['arch'] == 'win32':
			py_cmd.insert(0, 'wine')
		else: # win64
			py_cmd.insert(0, 'wine64')

		# Launch server
		self.__launch_wine__(py_cmd)


	def __read_output_from_pipe__(self, pipe, funcs):

		for line in iter(pipe.readline, b''):
			for func in funcs:
				func(line.decode('utf-8'))
		pipe.close()


	def __launch_wine__(self, command_list):

		self.wine_p = subprocess.Popen(
			command_list,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = False,
			preexec_fn = os.setsid,
			close_fds = True,
			bufsize = 1
			)

# wineserver first
# log via reverse xmlrpc

		print([p for p in psutil.process_iter() if self.id in p.cmdline()])
		self.python_proc = [p for p in psutil.process_iter() if self.id in p.cmdline()][0]
		print(self.python_proc)


		q = Queue()

		stdout_thread = Thread(
			target = self.__read_output_from_pipe__, args = (self.wine_p.stdout, [q.put, self.log.out])
			)

		stderr_thread = Thread(
			target = self.__read_output_from_pipe__, args = (self.wine_p.stderr, [q.put, self.log.err])
			)

		for t in (stdout_thread, stderr_thread):
			t.daemon = True
			t.start()

		self.wine_p.wait()

		for t in (stdout_thread, stderr_thread):
			t.join()

		q.put(None)


	def __server_stop__(self):

		# os.killpg(os.getpgid(self.wine_p.pid), signal.SIGTERM)
		os.killpg(os.getpgid(self.python_proc.pid), signal.SIGTERM)


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
