# ZUGBRUECKE
# Calling routines in Windows DLLs from Python scripts running on unixlike systems
# https://github.com/pleiszenburg/zugbruecke
#
#	makefile: GNU makefile for project management
#
#	Required to run on platform / side: [UNIX]
#
# 	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>
#
# <LICENSE_BLOCK>
# The contents of this file are subject to the GNU Lesser General Public License
# Version 2.1 ("LGPL" or "License"). You may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
# https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
# specific language governing rights and limitations under the License.
# </LICENSE_BLOCK>


demo_dll:
	@(cd demo_dll; make clean; make; make install)

release:
	-rm dist/*
	-rm -r src/*.egg-info
	python setup.py sdist bdist_wheel
	gpg --detach-sign -a dist/zugbruecke*.whl
	gpg --detach-sign -a dist/zugbruecke*.tar.gz

install:
	pip install -r requirements.txt
	pip install .

install_link:
	pip install -r requirements.txt
	pip install -e .

test:
	echo $PWD
	find . | grep -vi git
	pytest
