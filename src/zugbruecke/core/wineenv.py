# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/wineenv.py: Setting up a Python environment in Wine

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
# SETUP ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


def setup_wine_pip(arch, version, directory):

	# Download get-pip.py into memory
	getpip_req = urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py')
	getpip_bin = getpip_req.read()
	getpip_req.close()

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

	# Name of target subfolder
	pydir = '%s-python%s' % (arch, version)

	# Target directory
	target_directory = os.path.join(directory, pydir)

	# Is there a pre-existing Python installation with identical parameters?
	preexisting = os.path.isfile(os.path.join(target_directory, 'python.exe'))

	# Is there a preexisting installation and should it be overwritten?
	if preexisting and overwrite:
		# Delete folder
		shutil.rmtree(target_directory)

	# Make sure the target directory exists
	if not os.path.exists(directory):
		# Create folder
		os.makedirs(directory)

	# Get (potentially future) path of Python standard library
	library_path = os.path.join(target_directory, 'Lib')

	# Only do if Python is not there OR if should be overwritten
	if overwrite or not preexisting:

		# Generate in-memory file-like-object
		archive_zip = BytesIO()

		# Download zip file from Python website into file-like-object
		archive_req = urllib.request.urlopen(
			'https://www.python.org/ftp/python/%s/%s' % (version, pyarchive)
			)
		archive_zip.write(archive_req.read())
		archive_req.close()

		# Unpack from memory to disk
		f = zipfile.ZipFile(archive_zip)
		f.extractall(path = target_directory) # Directory created if required
		f.close()

		# Get path of Python library zip
		library_zip_path = os.path.join(target_directory, 'python%s%s.zip' % (
			version.split('.')[0], version.split('.')[1]
			))

		# Unpack Python library from embedded zip on disk
		f = zipfile.ZipFile(library_zip_path, 'r')
		f.extractall(path = library_path) # Directory created if required
		f.close()

		# Remove Python library zip from disk
		os.remove(library_zip_path)

	# Get wine-python site-packages path
	sitepackage_path = os.path.join(library_path, 'site-packages')

	# Create site-packages folder if it does not exist
	if not os.path.exists(sitepackage_path):
		# Create folder
		os.makedirs(sitepackage_path)

	# Package path in wine-python site-packages
	wine_pkg_path = os.path.abspath(os.path.join(sitepackage_path, 'zugbruecke'))

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
