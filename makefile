# ZUGBRUECKE
# Calling routines in Windows DLLs from Python scripts running on unixlike systems
# https://github.com/pleiszenburg/zugbruecke
#
#	makefile: GNU makefile for project management
#
#	Required to run on platform / side: [UNIX]
#
# 	Copyright (C) 2017-2021 Sebastian M. Ernst <ernst@pleiszenburg.de>
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

black:
	black .

clean:
	-rm -r build/*
	-rm -r dist/*
	coverage erase
	make clean_py
	make clean_dll
clean_py:
	find src/ tests/ -name '*.pyc' -exec rm -f {} +
	find src/ tests/ -name '*.pyo' -exec rm -f {} +
	find src/ tests/ -name '*~' -exec rm -f {} +
	find src/ tests/ -name '__pycache__' -exec rm -fr {} +
clean_dll:
	find src/ tests/ -name '*.dll' -exec rm -f {} +

release_clean:
	make clean
	-rm -r src/*.egg-info

# dll: # TODO move to example folder
# 	@(cd demo_dll; make clean; make; make install)

docu:
	@(cd docs; make clean; make html)

release:
	make release_clean
	python setup.py sdist bdist_wheel
	gpg --detach-sign -a dist/zugbruecke*.whl
	gpg --detach-sign -a dist/zugbruecke*.tar.gz

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done

upload_test:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc -r pypitest ; \
	done

install:
	pip install -U -e .[dev]
	WENV_ARCH=win32 wenv init
	WENV_ARCH=win32 wenv pip install -r requirements_test.txt
	WENV_ARCH=win32 wenv init_coverage
	WENV_ARCH=win64 wenv init
	WENV_ARCH=win64 wenv pip install -r requirements_test.txt
	WENV_ARCH=win64 wenv init_coverage

test:
	make docu
	make test_quick

test_quick:
	make clean
	python -m tests.lib.build
	make clean_py
	WENV_ARCH=win32 wenv pytest --hypothesis-show-statistics
	make clean_py
	WENV_ARCH=win64 wenv pytest --hypothesis-show-statistics
	make clean_py
	pytest --cov=zugbruecke --cov-config=setup.cfg --hypothesis-show-statistics # --capture=no
	# mv .coverage .coverage.e9.0 ; coverage combine ; coverage html # TODO fix!
