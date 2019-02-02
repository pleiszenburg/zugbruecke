# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/data/mem_definition.py: (Un-) packing of memory definitions

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

import ctypes
from pprint import pformat as pf
#import traceback


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS: Memory content packing and unpacking
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class memory_definition_class():


	def pack_definition_memsync(self, memsync_d_list):

		return [self.__pack_memsync_definition_dict__(memsync_d) for memsync_d in memsync_d_list]


	def unpack_definition_memsync(self, memsync_d_list):

		return [self.__unpack_memsync_definition_dict__(memsync_d) for memsync_d in memsync_d_list]


	def __pack_memsync_definition_dict__(self, memsync_d):

		# Keep everything, which is not private (does not start with '_')
		return {key: memsync_d[key] for key in memsync_d.keys() if not key.startswith('_')}


	def __unpack_memsync_definition_dict__(self, memsync_d):

		# Null-terminated string - off by default
		if 'n' not in memsync_d.keys():
			memsync_d['n'] = False

		# Compile length function
		if 'f' in memsync_d.keys():
			memsync_d['_f'] = eval(memsync_d['f']) # HACK?

		# Defaut type, if nothing is given, is unsigned byte
		if 't' not in memsync_d.keys():
			memsync_d['t'] = 'c_ubyte'

		# Get actual type class - if it is not a ctypes member, try struct cache
		memsync_d['_t'] = getattr(ctypes, memsync_d['t'], None)
		if memsync_d['_t'] is None:
			memsync_d['_t'] = self.cache_dict['struct_type'][memsync_d['t']]

		# Compute the size of type '_t'
		memsync_d['s'] = ctypes.sizeof(memsync_d['_t'])

		# Handle Unicode - off by default
		if 'w' not in memsync_d.keys():
			memsync_d['w'] = False

		return memsync_d
