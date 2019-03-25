# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	tests/test_paths.py: Converting paths between Unix and Wine/Windows formats

	Required to run on platform / side: [UNIX, WINE]

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

import pytest

from sys import platform
if any([platform.startswith(os_name) for os_name in ['linux', 'darwin', 'freebsd']]):
	import zugbruecke.ctypes as ctypes
	from zugbruecke.core.errors import wine_error
	IS_UNIX = True
elif platform.startswith('win'):
	IS_UNIX = False


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# TEST(s)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@pytest.mark.skipif(not IS_UNIX, reason = 'only relevant for unix side')
def test_path_unix_to_wine_abs():

	PATH_A = ('/foo/bar', 'Z:\\foo\\bar')
	assert ctypes._zb_path_unix_to_wine(PATH_A[0]) == PATH_A[1]


@pytest.mark.skipif(not IS_UNIX, reason = 'only relevant for unix side')
def test_path_unix_to_wine_rel():

	PATH_A = ('foo/bar', 'foo\\bar')
	path_out = ctypes._zb_path_unix_to_wine(PATH_A[0])
	assert path_out[:3] == 'Z:\\'
	assert path_out.endswith(PATH_A[1])
	assert len(path_out) > len(PATH_A[1]) + len('Z:\\')


@pytest.mark.skipif(not IS_UNIX, reason = 'only relevant for unix side')
def test_path_wine_to_unix_abs():

	PATH_A = 'C:\\'
	path_out = ctypes._zb_path_wine_to_unix(PATH_A)
	assert path_out.startswith('/')
	assert path_out.endswith('/c:/')
	assert len(path_out) > len('/') + len('/c:/')


@pytest.mark.skipif(not IS_UNIX, reason = 'only relevant for unix side')
def test_path_wine_to_unix_fail1():

	PATH_A = '\\doesnotexist'
	with pytest.raises(wine_error):
		path_out = ctypes._zb_path_wine_to_unix(PATH_A)


@pytest.mark.skipif(not IS_UNIX, reason = 'only relevant for unix side')
def test_path_wine_to_unix_fail2():

	PATH_A = 'c:\\doesnotexist'
	with pytest.raises(wine_error):
		path_out = ctypes._zb_path_wine_to_unix(PATH_A)
