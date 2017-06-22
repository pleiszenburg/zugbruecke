#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import subprocess
import sys


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CFG
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

arch = 'win32'
version = '3.5.3'


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# STUFF
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def wine_translate_unix2win(path):

	winepath_p = subprocess.Popen(
		['winepath', '-w', path],
		stdin = subprocess.PIPE,
		stdout = subprocess.PIPE
		)
	winepath_output = winepath_p.communicate()[0].decode(encoding = 'UTF-8')

	return winepath_output.strip()


def run_windows_python(win_python_script_name):

	# Change the environment for Wine: Architecture
	os.environ['WINEARCH'] = arch

	# Get location of this script file
	pycrosscall_cfg_path = os.path.join(os.path.expanduser('~'), '.pycrosscall')

	# Change the environment for Wine: Wine prefix / profile directory
	os.environ['WINEPREFIX'] = os.path.join(pycrosscall_cfg_path, arch + '-wine')

	# Python interpreter's directory seen from this script
	pydir_unix = os.path.join(pycrosscall_cfg_path, arch + '-python' + version)

	# Translate Python interpreter's Unix path into Wine path
	pydir_win = wine_translate_unix2win(pydir_unix)

	# Launch Python for Windows with script
	py_cmd = pydir_win + '\\python.exe ' + win_python_script_name
	subprocess.Popen('echo "%s" | wine cmd &' % py_cmd, shell = True)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	if len(sys.argv) > 1:
		run_windows_python(sys.argv[1])
