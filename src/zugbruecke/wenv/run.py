# -*- coding: utf-8 -*-

from .lib import env_class

import sys


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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class env_run_class(env_class):


	def __cmd_init__(self):
		# self.set_environment_variables()
		# self.setup_prefix()
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

		# No command was passed?
		if len(sys.argv) < 1:
			# Exit: Nothing to do
			return

		# Not (yet) a configuration call
		configure = False

		# Get command
		cmd = sys.argv[1]

		# Special commands
		special_list = ['init', 'help']

		# Special command
		if cmd in special_list:
			# Run matching routine
			getattr(self, '__cmd_%s__' % cmd)()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	env_run_class().cli()
