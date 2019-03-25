# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/wenv.py: Managing a Wine-Python environment

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
import sys
import urllib.request
import zipfile

from .core.config import config_class


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

HELP_STR = """wenv - the Wine Python environment

- wenv init: sets up an environment (including Python interpreter, pip and pytest)
- wenv help: prints this help text
- wenv python: the Python interpreter

Beyond that, the following scripts and modules are installed and available:

{scripts:s}
"""

COVERAGE_STARTUP = """
import coverage
coverage.process_startup()
"""

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
			if not isinstance(parameter, dict):
				raise TypeError('parameter is not a dictionary')
			self.p = parameter

		# Get Python environment paths
		self._path_dict_ = env_class.__get_wine_python_paths__(
			self.p['pythonprefix'], self.p['version']
			)
		# Get Python commands and scripts
		self._cmd_dict_ = env_class.__get_command_dict__(
			self._path_dict_['interpreter'], self._path_dict_['scripts']
			)
		# Get environment variables
		self._envvar_dict_ = env_class.__get_environment_variables__(
			self.p['wineprefix'], self.p['winedebug'], self.p['arch']
			)
		# Get Wine cmd names
		self._wine_dict_ = {'win32': 'wine', 'win64': 'wine64'}


	@staticmethod
	def __get_environment_variables__(wineprefix, winedebug, arch):

		return dict(
			WINEARCH = arch, # Architecture
			WINEPREFIX = wineprefix, # Wine prefix / directory
			WINEDLLOVERRIDES = 'mscoree=d', # Disable MONO: https://unix.stackexchange.com/a/191609
			WINEDEBUG = winedebug, # Wine debug level
			)


	@staticmethod
	def __get_command_dict__(interpreter_path, scripts_path):

		out = {'python': interpreter_path}

		if not os.path.exists(scripts_path):
			return out

		scripts = os.listdir(scripts_path)
		for script in scripts:
			if not script.lower().endswith('.exe'):
				continue
			out[script[:-4]] = os.path.join(scripts_path, script)

		return out


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
		# coverage
		coverage_path = os.path.join(scripts_path, 'coverage.exe')
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
			coverage = coverage_path,
			stdlibzip = stdlibzip_path,
			)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def setup_prefix(self, overwrite = False):

		if not isinstance(overwrite, bool):
			raise TypeError('overwrite is not a boolean')

		# Does it exist?
		if os.path.exists(self.p['wineprefix']):
			# Exit if overwrite flag is not set
			if not overwrite:
				return
			# Delete if overwrite is set
			shutil.rmtree(self.p['wineprefix'])

		# Start wine server into prepared environment
		subprocess.Popen(['wineboot', '-i']).wait()


	def setup_python(self, overwrite = False):

		if not isinstance(overwrite, bool):
			raise TypeError('overwrite is not a boolean')

		# File name for python stand-alone zip file
		pyarchive = 'python-%s-embed-%s.zip' % (
			self.p['version'],
			'amd64' if self.p['arch'] == 'win64' else self.p['arch']
			)
		# Compute full URL of Python stand-alone zip file
		pyurl = 'https://www.python.org/ftp/python/%s/%s' % (self.p['version'], pyarchive)

		# Is there a pre-existing Python installation with identical parameters?
		preexisting = os.path.isfile(self._path_dict_['interpreter'])

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
			with zipfile.ZipFile(self._path_dict_['stdlibzip'], 'r') as f:
				f.extractall(path = self._path_dict_['lib']) # Directory created if required
			# Remove Python library zip from disk
			os.remove(self._path_dict_['stdlibzip'])

		# Create site-packages folder if it does not exist
		if not os.path.exists(self._path_dict_['sitepackages']):
			# Create folder
			os.makedirs(self._path_dict_['sitepackages'])

		# Package path in wine-python site-packages
		wine_pkg_path = os.path.abspath(os.path.join(self._path_dict_['sitepackages'], 'zugbruecke'))

		# Package path in unix-python site-packages
		unix_pkg_path = os.path.abspath(os.path.dirname(__file__))

		# If package has not been linked into site-packages ...
		if not os.path.exists(wine_pkg_path):
			# Link zugbruecke package into wine-python site-packages
			os.symlink(unix_pkg_path, wine_pkg_path)


	def setup_pip(self):

		# Exit if it exists
		if os.path.isfile(self._path_dict_['pip']):
			return

		# Download get-pip.py into memory
		with urllib.request.urlopen('https://bootstrap.pypa.io/get-pip.py') as u:
			getpip_bin = u.read()

		# Start Python on top of Wine
		proc_getpip = subprocess.Popen(['wenv', 'python'], stdin = subprocess.PIPE)

		# Pipe script into interpreter and get feedback
		proc_getpip.communicate(input = getpip_bin)


	def setup_pytest(self):

		# Exit if it exists
		if os.path.isfile(self._path_dict_['pytest']):
			return

		# Run pip install
		subprocess.Popen(['wenv', 'pip', 'install', 'pytest']).wait()


	def setup_coverage(self):

		# Exit if it exists
		if os.path.isfile(self._path_dict_['coverage']):
			return

		# Run pip install
		subprocess.Popen(['wenv', 'pip', 'install', 'coverage']).wait()

		# Ensure that coverage is started with the Python interpreter
		siteconfig_path = os.path.join(self._path_dict_['sitepackages'], 'sitecustomize.py')
		if os.path.isfile(siteconfig_path):
			with open(siteconfig_path, 'r') as f:
				siteconfig_cnt = f.read(COVERAGE_STARTUP)
			if COVERAGE_STARTUP in siteconfig_cnt:
				return
		with open(siteconfig_path, 'w') as f:
			f.write(COVERAGE_STARTUP)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def set_environment_variables(self):

		for k, v in self._envvar_dict_.items():
			os.environ[k] = v


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def __cmd_init__(self):
		self.set_environment_variables()
		self.setup_prefix()
		self.setup_python()
		self.setup_pip()
		self.setup_pytest()
		self.setup_coverage()


	def __cmd_help__(self):
		sys.stdout.write(HELP_STR.format(scripts = '\n'.join([
			'- wenv {script:s}'.format(script = key)
			for key in sorted(self._cmd_dict_.keys())
			if key != 'python'
			])))
		sys.stdout.flush()


	def cli(self):

		def prefix(data, options = False):
			return '___%d___%s' % ((1 if options else 0), data)
		def push_return(data):
			sys.stdout.write(data)
			sys.stdout.flush()
			sys.exit()

		# No command was passed?
		if len(sys.argv) < 2:
			# Exit: Nothing to do
			return

		# Not (yet) a configuration call
		configure = False
		# Are there one or more arguments / options?
		if len(sys.argv) >= 3:
			# Is this a configuration call?
			if sys.argv[2] == '--configure':
				# Re-set flag
				configure = True

		# Get command
		cmd = sys.argv[1]

		# Special commands
		special_list = ['init', 'help']
		# Special command, first stage?
		if configure and (cmd in special_list):
			# Push new Python command for "interactive" second stage
			push_return(prefix(
				'python3 -m zugbruecke.wenv %s' % cmd, options = False
				))
		# Special command, second stage?
		if not configure and (cmd in special_list):
			# Run matching routine
			getattr(self, '__cmd_%s__' % cmd)()
			# Nothing more to do, leave
			return

		# If the command is unknown ...
		if configure and (cmd not in self._cmd_dict_.keys()):
			push_return(prefix('echo Unknown command or script: "%s"' % cmd, options = False))

		# Nothing more to do
		if not configure:
			return

		# Prepare environment variables for shell export
		cmd_list = ['%s=%s' % (k, v) for k, v in self._envvar_dict_.items()]
		# Append actual "interactive" command
		cmd_list.append(prefix(
			'%s "%s"' % (self._wine_dict_[self.p['arch']], self._cmd_dict_[cmd]),
			options = True,
			))
		# Push command stack and leave
		push_return('#'.join(cmd_list))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	env_class().cli()
