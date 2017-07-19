# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	src/zugbruecke/core/path.py: Coverts paths fron Unix to Wine format and vv

	Required to run on platform / side: [WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

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
from ctypes import wintypes


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# WINDOWS DATATYPES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class ANSI_STRING(ctypes.Structure):
	"""
	https://msdn.microsoft.com/de-de/library/windows/hardware/ff540605.aspx

	typedef struct _STRING {
		USHORT Length;
		USHORT MaximumLength;
		PCHAR  Buffer;
	} ANSI_STRING, *PANSI_STRING;
	"""

	_fields_ = [
		('Length', wintypes.USHORT),
		('MaximumLength', wintypes.USHORT),
		('Buffer', wintypes.LPSTR)
		]


class UNICODE_STRING(ctypes.Structure):
	"""
	https://msdn.microsoft.com/de-de/library/windows/desktop/aa380518.aspx

	typedef struct _LSA_UNICODE_STRING {
		USHORT Length;
		USHORT MaximumLength;
		PWSTR  Buffer;
	} LSA_UNICODE_STRING, *PLSA_UNICODE_STRING, UNICODE_STRING, *PUNICODE_STRING;
	"""

	_fields_ = [
		('Length', wintypes.USHORT),
		('MaximumLength', wintypes.USHORT),
		('Buffer', wintypes.LPWSTR)
		]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# PATH CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class path_class:


	def __init__(self):

		# Define MaximumLength TODO does it make sense?
		# https://msdn.microsoft.com/en-us/library/aa365247.aspx#maxpath
		self.MAX_PATH = 260

		# https://github.com/wine-mirror/wine/blob/master/include/winternl.h
		self.FILE_OPEN_IF = 3

		# NTSTATUS CDECL wine_unix_to_nt_file_name(
		#	const ANSI_STRING *name, UNICODE_STRING *nt
		#	)
		self.__unix_to_wine__ = ctypes.cdll.ntdll.wine_unix_to_nt_file_name
		self.__unix_to_wine__.argtypes = (
			ctypes.POINTER(ANSI_STRING), ctypes.POINTER(UNICODE_STRING)
			)
		self.__unix_to_wine__.restype = ctypes.c_int32 # NTSTATUS https://msdn.microsoft.com/en-us/library/cc704588.aspx

		# @ cdecl wine_nt_to_unix_file_name(ptr ptr long long)
		# NTSYSAPI NTSTATUS CDECL wine_nt_to_unix_file_name(
		#	const UNICODE_STRING *nameW, ANSI_STRING *unix_name_ret,
		#	UINT disposition, BOOLEAN check_case
		# 	);
		self.__wine_to_unix__ = ctypes.cdll.ntdll.wine_nt_to_unix_file_name
		self.__wine_to_unix__.argtypes = (
			ctypes.POINTER(UNICODE_STRING), ctypes.POINTER(ANSI_STRING),
			wintypes.UINT, wintypes.BOOLEAN
			)
		self.__wine_to_unix__.restype = ctypes.c_int32 # NTSTATUS https://msdn.microsoft.com/en-us/library/cc704588.aspx


	def unix_to_wine(self, in_path):
		"""
		In: Absolute Unix path
		Out: Absolute Wine path
		"""

		if len(in_path) > self.MAX_PATH:
			raise # TODO

		in_path_astr_p = ctypes.pointer(self.__str_to_winastr__(in_path))
		out_oath_ustr_p = ctypes.pointer(self.__generate_ustr__())

		ntstatus = self.__unix_to_wine__(
			in_path_astr_p, out_oath_ustr_p
			)

		return(self.__winustr_to_str__(out_oath_ustr_p.contents))


	def wine_to_unix(self, in_path):
		"""
		In: Absolute Wine path
		Out: Absolute Unix path
		"""

		if len(in_path) > self.MAX_PATH:
			raise # TODO

		pass


	def __generate_astr__(self):

		return ANSI_STRING(
			0, self.MAX_PATH, ctypes.pointer(ctypes.create_string_buffer(self.MAX_PATH))
			)


	def __generate_ustr__(self):

		return UNICODE_STRING(
			0, self.MAX_PATH, ctypes.pointer(ctypes.create_unicode_buffer(self.MAX_PATH))
			)


	def __str_to_winastr__(self, in_str_u):
		"""
		In: Python unicode string
		Out: ANSI_STRING
		"""

		in_str_a = in_str_u.encode('utf-8')
		in_astr = self.__generate_astr__()
		in_astr.Length = len(in_str_a)
		in_astr.Buffer.contents[0:in_astr.Length] = in_str_a[:]

		return in_astr


	def __str_to_winustr__(self, in_str_u):
		"""
		In: Python unicode string
		Out: UNICODE_STRING
		"""

		in_ustr = self.__generate_ustr__()
		in_ustr.Length = len(in_str_u)
		in_ustr.Buffer.contents[0:in_str_u.Length] = in_str_u[:]

		return in_ustr


	def __winastr_to_str__(self, in_astr):
		"""
		In: ANSI_STRING
		Out: Python unicode string
		"""

		return in_astr[0:in_astr.Length].decode('utf-8')


	def __winustr_to_str__(self, in_ustr):
		"""
		In: UNICODE_STRING
		Out: Python unicode string
		"""

		return in_ustr[0:in_ustr.Length]
