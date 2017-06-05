# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import subprocess


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINE SESSION CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class wine_session_class:

	def __init__(self, session_id, session_log):

		self.id = session_id
		self.log = session_log

		self.log.out('wine session started')


	def terminate(self):

		self.log.out('wine session terminated')


	def translate_path_unix2win(self, path):

		winepath_p = subprocess.Popen(
			['winepath', '-w', path],
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
			)
		wine_out, wine_err = winepath_p.communicate()

		return wine_out.decode(encoding = 'UTF-8').strip(), wine_err.decode(encoding = 'UTF-8')
