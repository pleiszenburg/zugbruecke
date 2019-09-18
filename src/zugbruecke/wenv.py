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
from .core.log import c


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

COVERAGE_STARTUP = """
import coverage
coverage.process_startup()
"""

HELP_STR = """wenv - the Wine Python environment

{CLIS:s}

The following interpreters, scripts and modules are installed and available:

{SCRIPTS:s}
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
			self._p = config_class()
		else:
			if not isinstance(parameter, dict):
				raise TypeError('parameter is not a dictionary')
			self._p = parameter

		# Init internal dicts
		self._init_dicts()


	def _init_dicts(self):

		# Init Wine cmd names
		self._wine_dict = {'win32': 'wine', 'win64': 'wine64'}

		# Init Python environment paths
		self._init_path_dict()
		# Init Python commands and scripts
		self._init_cmd_dict()
		# Init internal CLI commands
		self._init_cli_dict()
		# Init environment variables
		self._init_envvar_dict()


	def _init_path_dict(self):

		version_string = ''.join(self._p['version'].split('.')[0:2])

		# python standard library
		lib_path = os.path.join(self._p['pythonprefix'], 'Lib')
		# site-packages
		sitepackages_path = os.path.join(lib_path, 'site-packages')
		# python interpreter
		interpreter_path = os.path.join(self._p['pythonprefix'], 'python.exe')
		# scripts
		scripts_path = os.path.join(self._p['pythonprefix'], 'Scripts')
		# pip
		pip_path = os.path.join(scripts_path, 'pip.exe')
		# pytest
		pytest_path = os.path.join(scripts_path, 'pytest.exe')
		# coverage
		coverage_path = os.path.join(scripts_path, 'coverage.exe')
		# stdlib zip filename
		stdlibzip_path = os.path.join(self._p['pythonprefix'], 'python%s.zip' % version_string)
		# pth filename (library path)
		pth_path = os.path.join(self._p['pythonprefix'], 'python%s._pth' % version_string)

		self._path_dict = dict(
			lib = lib_path,
			sitepackages = sitepackages_path,
			scripts = scripts_path,
			interpreter = interpreter_path,
			pip = pip_path,
			pytest = pytest_path,
			coverage = coverage_path,
			stdlibzip = stdlibzip_path,
			pth = pth_path,
			)


	def _init_cmd_dict(self):

		out = {'python': self._path_dict['interpreter']} # TODO check!

		if not os.path.exists(self._path_dict['scripts']):
			self._cmd_dict = out
			return

		scripts = os.listdir(self._path_dict['scripts'])
		for script in scripts:
			if not script.lower().endswith('.exe'):
				continue
			out[script[:-4]] = os.path.join(self._path_dict['scripts'], script)

		self._cmd_dict = out


	def _init_cli_dict(self):

		self._cli_dict = {
			item[5:]: getattr(self, item)
			for item in dir(self)
			if item.startswith('_cli_') and hasattr(getattr(self, item), '__call__')
			}


	def _init_envvar_dict(self):

		self._envvar_dict = {k: os.environ[k] for k in os.environ.keys()} # HACK Required for Travis CI
		self._envvar_dict.update(dict(
			WINEARCH = self._p['arch'], # Architecture
			WINEPREFIX = self._p['wineprefix'], # Wine prefix / directory
			WINEDLLOVERRIDES = 'mscoree=d', # Disable MONO: https://unix.stackexchange.com/a/191609
			WINEDEBUG = self._p['winedebug'], # Wine debug level
			PYTHONHOME = self._p['pythonprefix'], # Python home for Wine Python (can be a Unix path)
			))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ENSURE ENVIRONMENT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def ensure(self):

		self.setup_prefix()
		self.setup_python()
		self.wine_47766_workaround() # must run after setup_python and before setup_pip
		self.setup_pip()
		self.setup_pytest()
		self.setup_coverage()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def setup_prefix(self, overwrite = False):

		if not isinstance(overwrite, bool):
			raise TypeError('overwrite is not a boolean')

		# Does it exist?
		if os.path.exists(self._p['wineprefix']):
			# Exit if overwrite flag is not set
			if not overwrite:
				return
			# Delete if overwrite is set
			shutil.rmtree(self._p['wineprefix'])

		os.makedirs(self._p['wineprefix']) # HACK Wine on Travis CI expects folder to exist

		# Start wine server into prepared environment
		proc = subprocess.Popen(
			['wine', 'wineboot', '-i'],
			stdout = subprocess.PIPE, stderr = subprocess.PIPE,
			env = self._envvar_dict
			)
		out, err = proc.communicate()
		print(out.decode('utf-8').strip())
		print(err.decode('utf-8').strip())
		if proc.returncode != 0:
			sys.exit(1)


	def setup_python(self, overwrite = False):

		if not isinstance(overwrite, bool):
			raise TypeError('overwrite is not a boolean')

		# File name for python stand-alone zip file
		pyarchive = 'python-%s-embed-%s.zip' % (
			self._p['version'],
			'amd64' if self._p['arch'] == 'win64' else self._p['arch']
			)
		# Compute full URL of Python stand-alone zip file
		pyurl = 'https://www.python.org/ftp/python/%s/%s' % (self._p['version'], pyarchive)

		# Is there a pre-existing Python installation with identical parameters?
		preexisting = os.path.isfile(self._path_dict['interpreter'])

		# Is there a preexisting installation and should it be overwritten?
		if preexisting and overwrite:
			# Delete folder
			shutil.rmtree(self._p['pythonprefix'])

		# Make sure the target directory exists
		if not os.path.exists(self._p['pythonprefix']):
			# Create folder
			os.makedirs(self._p['pythonprefix'])

		# Only do if Python is not there OR if should be overwritten
		if overwrite or not preexisting:

			# Generate in-memory file-like-object
			archive_zip = BytesIO()
			# Download zip file from Python website into file-like-object
			with urllib.request.urlopen(pyurl) as u:
				archive_zip.write(u.read())
			# Unpack from memory to disk
			with zipfile.ZipFile(archive_zip) as f:
				f.extractall(path = self._p['pythonprefix']) # Directory created if required

			# Unpack Python library from embedded zip on disk
			with zipfile.ZipFile(self._path_dict['stdlibzip'], 'r') as f:
				f.extractall(path = self._path_dict['lib']) # Directory created if required
			# Remove Python library zip from disk
			os.remove(self._path_dict['stdlibzip'])

			# HACK: Fix library path in pth-file (CPython >= 3.6)
			with open(self._path_dict['pth'], 'w') as f:
				f.write('Lib\n.\n\n# Uncomment to run site.main() automatically\nimport site\n')

		# Create site-packages folder if it does not exist
		if not os.path.exists(self._path_dict['sitepackages']):
			# Create folder
			os.makedirs(self._path_dict['sitepackages'])

		# Package path in wine-python site-packages
		wine_pkg_path = os.path.abspath(os.path.join(self._path_dict['sitepackages'], 'zugbruecke'))

		# Package path in unix-python site-packages
		unix_pkg_path = os.path.abspath(os.path.dirname(__file__))

		# If package has not been linked into site-packages ...
		if not os.path.exists(wine_pkg_path):
			# Link zugbruecke package into wine-python site-packages
			os.symlink(unix_pkg_path, wine_pkg_path)


	def wine_47766_workaround(self):
		"""
		PathAllocCanonicalize treats path segments start with dots wrong.
		https://bugs.winehq.org/show_bug.cgi?id=47766
		"""

		is_clean = lambda path: not any([seg.startswith('.') for seg in path.split(os.path.sep)])

		pythonprefix = os.path.abspath(self._p['pythonprefix'])

		if pythonprefix != self._p['pythonprefix']:
			self._p['pythonprefix'] = pythonprefix
			self._init_dicts()

		if is_clean(self._p['pythonprefix']):
			return

		import tempfile, hashlib
		link_path = os.path.join(
			tempfile.gettempdir(),
			'wenv-' + hashlib.sha256(self._p['pythonprefix'].encode('utf-8')).hexdigest()[:8],
			)
		if not is_clean(link_path):
			raise OSError('unable to create clean link path: "{LINK:s}"'.format(LINK = link_path))
		if not os.path.exists(link_path):
			os.symlink(self._p['pythonprefix'], link_path)
		if not os.path.exists(link_path):
			raise OSError('"{LINK:s}" could not be created'.format(LINK = link_path))
		if not os.path.islink(link_path):
			raise OSError('"{LINK:s}" is not a symlink'.format(LINK = link_path))
		if os.readlink(link_path) != pythonprefix:
			raise OSError('"{LINK:s}" points to the wrong source'.format(LINK = link_path))

		print('XXX %s XXX' % link_path) # XXX

		self._p['pythonprefix'] = link_path
		self._init_dicts()


	def setup_pip(self):

		# Exit if it exists
		if os.path.isfile(self._path_dict['pip']):
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
		if os.path.isfile(self._path_dict['pytest']):
			return

		# Run pip install
		subprocess.Popen(['wenv', 'pip', 'install', 'pytest']).wait()


	def setup_coverage(self):

		# Exit if it exists
		if os.path.isfile(self._path_dict['coverage']):
			return

		# Run pip install
		subprocess.Popen(['wenv', 'pip', 'install', 'coverage']).wait()
		subprocess.Popen(['wenv', 'pip', 'install', 'pytest-cov']).wait()


	def setup_coverage_activate(self):

		# Ensure that coverage is started with the Python interpreter
		siteconfig_path = os.path.join(self._path_dict['sitepackages'], 'sitecustomize.py')
		siteconfig_cnt = ''
		if os.path.isfile(siteconfig_path):
			with open(siteconfig_path, 'r') as f:
				siteconfig_cnt = f.read()
			if COVERAGE_STARTUP in siteconfig_cnt:
				return
		with open(siteconfig_path, 'w') as f:
			f.write(siteconfig_cnt + '\n' + COVERAGE_STARTUP)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

	def _cli_init(self):
		"sets up an environment (including Python interpreter, pip and pytest)"

		self.ensure()


	def _cli_init_coverage(self):
		"enables coverage analysis inside wenv"

		self.setup_coverage_activate()


	def _cli_help(self):
		"prints this help text"

		def colorize(text):
			for color, key in (
				('GREEN', 'python'),
				('CYAN', 'pip'),
				('YELLOW', 'wheel'),
				('MAGENTA', 'pytest'),
				('MAGENTA', 'py.test'),
				):
				text = text.replace(key, c[color] + key + c['RESET'])
			return text

		sys.stdout.write(HELP_STR.format(
			CLIS = '\n'.join([
				'- wenv {CLI:s}: {HELP:s}'.format(
					CLI = key,
					HELP = self._cli_dict[key].__doc__,
					)
				for key in sorted(self._cli_dict.keys())
				]),
			SCRIPTS = colorize('\n'.join([
				'- wenv {SCRIPT:s}'.format(
					SCRIPT = key,
					)
				for key in sorted(self._cmd_dict.keys())
				]))
			))
		sys.stdout.flush()


	def cli(self):

		# No command passed
		if len(sys.argv) < 2:
			sys.stderr.write('There was no command passed.\n')
			sys.stderr.flush()
			sys.exit(1)

		# Separate command and arguments
		cmd, param = sys.argv[1], sys.argv[2:]

		# Special CLI command
		if cmd in self._cli_dict.keys():
			self._cli_dict[cmd]()
			sys.exit(0)

		# Command is unknown
		if cmd not in self._cmd_dict.keys():
			sys.stderr.write('Unknown command or script: "{CMD:s}"\n'.format(CMD = cmd))
			sys.stderr.flush()
			sys.exit(1)

		# Get Wine depending on arch
		wine = self._wine_dict[self._p['arch']]

		self.wine_47766_workaround()

		# Replace this process with Wine
		os.execvpe(
			wine,
			(wine, self._cmd_dict[cmd]) + tuple(param), # Python 3.4: No in-place unpacking of param
			self._envvar_dict
			)

	def shebang(self):
		"""Working around a lack of Unix specification ...
		https://stackoverflow.com/q/4303128/1672565
		https://unix.stackexchange.com/q/63979/28301
		https://lists.gnu.org/archive/html/bug-sh-utils/2002-04/msg00020.html
		"""

		if len(sys.argv) < 2:
			raise OSError('entry point meant to be used as a shebang but no file name was provided')

		# Get Wine depending on arch
		wine = self._wine_dict[self._p['arch']]

		self.wine_47766_workaround()

		# Replace this process with Wine
		os.execvpe(
			wine,
			(wine, self._cmd_dict['python'], sys.argv[1]),
			self._envvar_dict
			)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI EXPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def cli():

	env_class().cli()


def shebang():

	env_class().shebang()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	cli()
