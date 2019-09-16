# -*- coding: utf-8 -*-

from .lib import env_class

import sys


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLI HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class env_configure_class(env_class):


	def cli(self):

		def prefix(data, options = False):
			return '___%d___%s' % ((1 if options else 0), data)
		def push_return(data):
			sys.stdout.write(data)
			sys.stdout.flush()
			sys.exit()

		# No command was passed?
		if len(sys.argv) < 1:
			# Exit: Nothing to do
			return

		# Get command
		cmd = sys.argv[1]

		# Special commands
		special_list = ['init', 'help']

		# Special command, first stage?
		if cmd in special_list:
			# Push new Python command for "interactive" second stage
			push_return(prefix(
				'python3 -m zugbruecke.wenv.run %s' % cmd, options = False
				))

		# If the command is unknown ...
		if cmd not in self._cmd_dict_.keys():
			push_return(prefix(
				'echo Unknown command or script: "%s"' % cmd, options = False
				))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MAIN
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == '__main__':

	env_configure_class().cli()
