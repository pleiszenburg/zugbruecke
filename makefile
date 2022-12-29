# ZUGBRUECKE
# Calling routines in Windows DLLs from Python scripts running on unixlike systems
# https://github.com/pleiszenburg/zugbruecke
#
#	makefile: GNU makefile for project management
#
#	Required to run on platform / side: [UNIX]
#
# 	Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>
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

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# LIB
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

_clean_coverage:
	coverage erase

_clean_dll:
	find src/ tests/ benchmark/ -name '*.dll' -exec rm -f {} +

_clean_py:
	find src/ tests/ benchmark/ -name '*.pyc' -exec rm -f {} +
	find src/ tests/ benchmark/ -name '*.pyo' -exec rm -f {} +
	find src/ tests/ benchmark/ -name '*~' -exec rm -f {} +
	find src/ tests/ benchmark/ -name '__pycache__' -exec rm -fr {} +

_clean_release:
	-rm -r build/*
	-rm -r dist/*

# examples:
# 	@(cd examples; make clean; make; make install)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ENTRY POINTS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

black:
	black .

benchmark:
	make clean
	-rm benchmark/data.raw
	-rm docs/source/benchmark_*.rst
	python -m tests.lib.build benchmark
	python -m tests.lib.benchmark wine
	python -m tests.lib.benchmark unix
	python -m tests.lib.benchmark table
	make docs

clean:
	make _clean_release
	make _clean_coverage
	make _clean_py
	make _clean_dll

docs:
	@(cd docs; make clean; make html)

install:
	pip install -U -e .[dev,test]
	python -m tests.lib.install

release:
	make clean
	flit build
	gpg --detach-sign -a dist/zugbruecke*.whl
	gpg --detach-sign -a dist/zugbruecke*.tar.gz

upload:
	for filename in $$(ls dist/*.tar.gz dist/*.whl) ; do \
		twine upload $$filename $$filename.asc ; \
	done

test:
	make clean
	python -m tests.lib.build tests
	python -m tests.lib.run wine
	python -m tests.lib.run unix
	mv .coverage .coverage.00 ; coverage combine ; coverage html -i

.PHONY: docs
.PHONY: benchmark
