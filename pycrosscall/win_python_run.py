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


def wine_translate(path):
	
	winepath_p = subprocess.Popen(
		['winepath', '-w', path],
		stdin = subprocess.PIPE,
		stdout = subprocess.PIPE
		)
	winepath_output = winepath_p.communicate()[0].decode(encoding = 'UTF-8')

	return winepath_output.strip()



def run_windows_python(script_name):
	
	# Get location of this script file
	script_path = os.path.split(os.path.realpath(__file__))[0]
	
	# Change the environment for Wine
	os.environ['WINEARCH'] = arch
	os.environ['WINEPREFIX'] = os.path.join(script_path, arch + '-wine')
	
	# Python interpreter's directory seen from this script
	pydir = os.path.join(script_path, arch + '-python' + version)
	
	# Translate Python interpreter's Unix path into Wine path
	pydir_wine = wine_translate(pydir)
	
	# Launch Python for Windows with script
	py_cmd = pydir_wine + '\\python.exe ' + script_name
	subprocess.Popen('echo "%s" | wine cmd &' % py_cmd, shell = True)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
	
	if len(sys.argv) > 1:
		run_windows_python(sys.argv[1])

