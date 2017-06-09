# -*- coding: utf-8 -*-


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

from distutils.core import setup


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# SETUP
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

setup(
	name = 'pycrosscall',
	packages = ['pycrosscall'],
	version = '0.0.1',
	description = 'Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD',
	author = 'Sebastian M. Ernst',
	author_email = 'ernst@pleiszenburg.de',
	url = 'https://github.com/s-m-e/pycrosscall',
	download_url = 'https://github.com/s-m-e/pycrosscall/archive/pycrosscall_0.0.1.tar.gz',
	keywords = ['ctypes', 'wine'],
	classifiers = []
)
