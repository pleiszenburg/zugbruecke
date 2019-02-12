# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/wenv/env.py: Class for managing a Wine-Python environment

	Required to run on platform / side: [UNIX]

	Copyright (C) 2017-2019 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

from io import BytesIO
import os
import shutil
import subprocess
import urllib.request
import zipfile


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE-PYTHON ENVIRONMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class env_class:


	def create_wine_prefix(dir_wineprefix):

		# Does it exist?
		if os.path.exists(dir_wineprefix):
			# Nothing to do
			return

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


	def __get_wine_python_paths__(arch, version, directory):

		# root path
		root_path = os.path.join(directory, '%s-python%s' % (arch, version))
		# python standard library
		lib_path = os.path.join(root_path, 'Lib')
		# site-packages
		sitepackages_path = os.path.join(lib_path, 'site-packages')
		# python interpreter
		interpreter_path = os.path.join(root_path, 'python.exe')
		# scripts
		scripts_path = os.path.join(root_path, 'Scripts')
		# pip
		pip_path = os.path.join(scripts_path, 'pip.exe')
		# pytest
		pytest_path = os.path.join(scripts_path, 'pytest.exe')
		# stdlib zip filename
		stdlibzip_path = os.path.join(
			root_path,
			'python%s%s.zip' % (version.split('.')[0], version.split('.')[1])
			)

		# Return dict
		return dict(
			root = root_path,
			lib = lib_path,
			sitepackages = sitepackages_path,
			scripts = scripts_path,
			interpreter = interpreter_path,
			pip = pip_path,
			pytest = pytest_path,
			stdlibzip = stdlibzip_path,
			)


	def setup_wine_pip(arch, version, directory):

		# Environment paths
		path_dict = __get_wine_python_paths__(arch, version, directory)

		# Exit if it exists
		if os.path.isfile(path_dict['pip']):
			return

		# Download get-pip.py into memory
		with urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py') as u:
			getpip_bin = u.read()

		# Start Python on top of Wine
		proc_getpip = subprocess.Popen(
			['wine-python'],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE,
			shell = False
			)

		# Pipe script into interpreter and get feedback
		getpip_out, getpip_err = proc_getpip.communicate(input = getpip_bin)


	def setup_wine_python(arch, version, directory, overwrite = False):

		# File name for python stand-alone zip file
		pyarchive = 'python-%s-embed-%s.zip' % (version, 'amd64' if arch == 'win64' else arch)
		# Compute full URL of Python stand-alone zip file
		pyurl = 'https://www.python.org/ftp/python/%s/%s' % (version, pyarchive)
		# Environment paths
		path_dict = __get_wine_python_paths__(arch, version, directory)

		# Is there a pre-existing Python installation with identical parameters?
		preexisting = os.path.isfile(path_dict['interpreter'])

		# Is there a preexisting installation and should it be overwritten?
		if preexisting and overwrite:
			# Delete folder
			shutil.rmtree(path_dict['root'])

		# Make sure the target directory exists
		if not os.path.exists(directory):
			# Create folder
			os.makedirs(directory)

		# Only do if Python is not there OR if should be overwritten
		if overwrite or not preexisting:

			# Generate in-memory file-like-object
			archive_zip = BytesIO()
			# Download zip file from Python website into file-like-object
			with urllib.request.urlopen(pyurl) as u:
				archive_zip.write(u.read())
			# Unpack from memory to disk
			with zipfile.ZipFile(archive_zip) as f:
				f.extractall(path = path_dict['root']) # Directory created if required

			# Unpack Python library from embedded zip on disk
			with zipfile.ZipFile(path_dict['stdlibzip'], 'r') as f:
				f.extractall(path = path_dict['lib']) # Directory created if required
			# Remove Python library zip from disk
			os.remove(path_dict['stdlibzip'])

		# Create site-packages folder if it does not exist
		if not os.path.exists(path_dict['sitepackages']):
			# Create folder
			os.makedirs(path_dict['sitepackages'])

		# Package path in wine-python site-packages
		wine_pkg_path = os.path.abspath(os.path.join(path_dict['sitepackages'], 'zugbruecke'))

		# Package path in unix-python site-packages
		unix_pkg_path = os.path.abspath(os.path.join(
			os.path.dirname(__file__), os.path.pardir
			))

		# If package has not been linked into site-packages ...
		if not os.path.exists(wine_pkg_path):
			# Link zugbruecke package into wine-python site-packages
			os.symlink(unix_pkg_path, wine_pkg_path)


	def set_wine_env(wineprefix, arch):

		# Change the environment for Wine: Architecture
		os.environ['WINEARCH'] = arch

		# Change the environment for Wine: Wine prefix / profile directory
		os.environ['WINEPREFIX'] = wineprefix

		# Disable MONO: https://unix.stackexchange.com/a/191609
		os.environ['WINEDLLOVERRIDES'] = 'mscoree=d'
