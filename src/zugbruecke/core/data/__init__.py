# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/data/__init__.py: Arguments, return values and memory

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

from ctypes import _FUNCFLAG_CDECL

from .arg_contents import arguments_contents_class
from .arg_definition import arguments_definition_class
from .mem_contents import memory_contents_class
from .mem_definition import memory_definition_class

from ..const import _FUNCFLAG_STDCALL


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: DATA
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class data_class(
	arguments_contents_class,
	arguments_definition_class,
	memory_contents_class,
	memory_definition_class
	):


	cache_dict = {
		'func_type': {
			_FUNCFLAG_CDECL: {},
			_FUNCFLAG_STDCALL: {}
			},
		'func_handle': {},
		'struct_type': {}
		}


	def __init__(self, log, is_server, callback_client = None, callback_server = None):

		self.log = log
		self.is_server = is_server

		self.callback_client = callback_client
		self.callback_server = callback_server
