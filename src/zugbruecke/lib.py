# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/lib.py: General purpose routines

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

import os
import random
import shutil
import socket
import tempfile
import urllib.request
import zipfile


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LIBRARY ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def get_free_port():

	s = socket.socket()
	s.bind(('', 0))
	port = s.getsockname()[1]
	s.close()

	return port


def get_location_of_file(filename = ''):

	if filename == '':
		filename = __file__

	return os.path.split(os.path.realpath(filename))[0]


def get_randhashstr(dig):

	# Return hash string with dig digits
	return (('%0' + str(dig) + 'x') % random.randrange(16**dig))


def generate_session_id():

	# A session id by default is an 8 digit hash string
	return get_randhashstr(8)


def setup_wine_pip(arch, version, directory, overwrite = False):

	pass


def setup_wine_python(arch, version, directory, overwrite = False):

	# File name for python stand-alone zip file
	pyarchive = 'python-%s-embed-%s.zip' % (version, arch)

	# Name of target subfolder
	pydir = '%s-python%s' % (arch, version)

	# Target directory
	target_directory = os.path.join(directory, pydir)

	# Target location of python.exe
	python_exe_path = os.path.join(target_directory, 'python.exe')

	# Is there a pre-existing Python installation with identical parameters?
	preexisting = os.path.isfile(python_exe_path)

	# Is there a preexisting installation and should it be overwritten?
	if preexisting and overwrite:

		# Delete folder
		shutil.rmtree(path)

	# Make sure the target directory exists
	if not os.path.exists(directory):
		os.makedirs(directory)

	# Only do if Python is not there OR if should be overwritten
	if overwrite or not preexisting:

		# Path to zip archive
		archive_path = os.path.join(directory, pyarchive)

		# Download zip file from Python website into directory
		urllib.request.urlretrieve(
			'https://www.python.org/ftp/python/%s/%s' % (version, pyarchive),
			archive_path
			)

		# Unpack
		f = zipfile.ZipFile(archive_path, mode = 'r')
		f.extractall(path = target_directory)
		f.close()

		# Delete zip file
		os.remove(os.path.join(directory, pyarchive))
