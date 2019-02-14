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

from ..core.config import config_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE-PYTHON ENVIRONMENT CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class env_class:


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def __init__(self, parameter = None):

		# Get config
		if parameter is None:
			self.p = config_class()
		else:
			self.p = parameter

		# Get paths
		self.paths = env_class.__get_wine_python_paths__(self.p['pythonprefix'], self.p['version'])

		# Set environment variables
		env_class.__init_environment_variables__(self.p['wineprefix'], self.p['arch'])


	@staticmethod
	def __init_environment_variables__(wineprefix, arch):

		# Change the environment for Wine: Architecture
		os.environ['WINEARCH'] = arch

		# Change the environment for Wine: Wine prefix / profile directory
		os.environ['WINEPREFIX'] = wineprefix

		# Disable MONO: https://unix.stackexchange.com/a/191609
		os.environ['WINEDLLOVERRIDES'] = 'mscoree=d'


	@staticmethod
	def __get_wine_python_paths__(pythonprefix, version):

		# python standard library
		lib_path = os.path.join(pythonprefix, 'Lib')
		# site-packages
		sitepackages_path = os.path.join(lib_path, 'site-packages')
		# python interpreter
		interpreter_path = os.path.join(pythonprefix, 'python.exe')
		# scripts
		scripts_path = os.path.join(pythonprefix, 'Scripts')
		# pip
		pip_path = os.path.join(scripts_path, 'pip.exe')
		# pytest
		pytest_path = os.path.join(scripts_path, 'pytest.exe')
		# stdlib zip filename
		stdlibzip_path = os.path.join(
			pythonprefix,
			'python%s%s.zip' % (version.split('.')[0], version.split('.')[1])
			)

		# Return dict
		return dict(
			lib = lib_path,
			sitepackages = sitepackages_path,
			scripts = scripts_path,
			interpreter = interpreter_path,
			pip = pip_path,
			pytest = pytest_path,
			stdlibzip = stdlibzip_path,
			)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def create_wine_prefix(self, overwrite = False):

		# Does it exist?
		if os.path.exists(self.p['wineprefix']):
			# Exit if overwrite flag is not set
			if not overwrite:
				return
			# Delete if overwrite is set
			shutil.rmtree(self.p['wineprefix'])

		# Start wine server into prepared environment
		subprocess.Popen(['wineboot', '-i']).wait()


	def setup_wine_python(self, overwrite = False):

		# File name for python stand-alone zip file
		pyarchive = 'python-%s-embed-%s.zip' % (
			self.p['version'],
			'amd64' if self.p['arch'] == 'win64' else self.p['arch']
			)
		# Compute full URL of Python stand-alone zip file
		pyurl = 'https://www.python.org/ftp/python/%s/%s' % (self.p['version'], pyarchive)

		# Is there a pre-existing Python installation with identical parameters?
		preexisting = os.path.isfile(self.paths['interpreter'])

		# Is there a preexisting installation and should it be overwritten?
		if preexisting and overwrite:
			# Delete folder
			shutil.rmtree(self.p['pythonprefix'])

		# Make sure the target directory exists
		if not os.path.exists(self.p['pythonprefix']):
			# Create folder
			os.makedirs(self.p['pythonprefix'])

		# Only do if Python is not there OR if should be overwritten
		if overwrite or not preexisting:

			# Generate in-memory file-like-object
			archive_zip = BytesIO()
			# Download zip file from Python website into file-like-object
			with urllib.request.urlopen(pyurl) as u:
				archive_zip.write(u.read())
			# Unpack from memory to disk
			with zipfile.ZipFile(archive_zip) as f:
				f.extractall(path = self.p['pythonprefix']) # Directory created if required

			# Unpack Python library from embedded zip on disk
			with zipfile.ZipFile(self.paths['stdlibzip'], 'r') as f:
				f.extractall(path = self.paths['lib']) # Directory created if required
			# Remove Python library zip from disk
			os.remove(self.paths['stdlibzip'])

		# Create site-packages folder if it does not exist
		if not os.path.exists(self.paths['sitepackages']):
			# Create folder
			os.makedirs(self.paths['sitepackages'])

		# Package path in wine-python site-packages
		wine_pkg_path = os.path.abspath(os.path.join(self.paths['sitepackages'], 'zugbruecke'))

		# Package path in unix-python site-packages
		unix_pkg_path = os.path.abspath(os.path.join(
			os.path.dirname(__file__), os.path.pardir
			))

		# If package has not been linked into site-packages ...
		if not os.path.exists(wine_pkg_path):
			# Link zugbruecke package into wine-python site-packages
			os.symlink(unix_pkg_path, wine_pkg_path)


	def setup_wine_pip(self):

		# Exit if it exists
		if os.path.isfile(self.paths['pip']):
			return

		# Download get-pip.py into memory
		with urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py') as u:
			getpip_bin = u.read()

		# Start Python on top of Wine
		proc_getpip = subprocess.Popen(['wine-python'], stdin = subprocess.PIPE)

		# Pipe script into interpreter and get feedback
		proc_getpip.communicate(input = getpip_bin)
