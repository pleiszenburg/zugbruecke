#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import os
import subprocess


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

	return winepath_output



def run_windows_python(parameter):
	
	# Get location of this script file
	script_path = os.path.split(os.path.realpath(__file__))[0]
	
	# Change the environment for Wine
	os.environ['WINEARCH'] = arch
	os.environ['WINEPREFIX'] = os.path.join(script_path, arch + '-wine')
	
	# Python interpreter's directory seen from this script
	pydir = os.path.join(script_path, arch + '-python' + version)
	
	# Translate Python interpreter's Unix path into Wine path
	pydir_wine = wine_translate(pydir)
	
	
	print(pydir_wine)
	
	
	#export WINEARCH="$arch"
	#export WINEPREFIX="$(pwd)/$arch-wine"
	#cd $arch-python$version
	#subprocess.Popen('echo "python dll_call.py %s" | wine cmd &' % options, shell = True)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# RUN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':
	
	run_windows_python(None)

