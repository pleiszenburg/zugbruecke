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

# Define MaximumLength TODO does it make sense?
# https://msdn.microsoft.com/en-us/library/aa365247.aspx#maxpath
MAX_PATH = 260


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

		# https://github.com/wine-mirror/wine/blob/master/include/winternl.h
		self.FILE_OPEN_IF = 3

		# BOOLEAN WINAPI RtlDosPathNameToNtPathName_U(
		#	PCWSTR dos_path,
		#	PUNICODE_STRING ntpath,
		#	PWSTR* file_part,
		#	CURDIR* cd
		#	)
		self.__dos_to_nt__ = ctypes.windll.ntdll.RtlDosPathNameToNtPathName_U
		self.__dos_to_nt__.argtypes = (
			ctypes.c_void_p,
			ctypes.c_void_p,
			ctypes.c_void_p,
			ctypes.c_void_p
			)
		self.__dos_to_nt__.restype = wintypes.BOOLEAN

		# NTSTATUS CDECL wine_unix_to_nt_file_name(
		#	const ANSI_STRING *name, UNICODE_STRING *nt
		#	)
		self.__unix_to_wine__ = ctypes.cdll.ntdll.wine_unix_to_nt_file_name
		self.__unix_to_wine__.argtypes = (
			ctypes.POINTER(ANSI_STRING), ctypes.POINTER(UNICODE_STRING)
			)
		self.__unix_to_wine__.restype = wintypes.LONG # NTSTATUS https://msdn.microsoft.com/en-us/library/cc704588.aspx

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
		self.__wine_to_unix__.restype = wintypes.LONG # NTSTATUS https://msdn.microsoft.com/en-us/library/cc704588.aspx


	def unix_to_wine(self, in_path):
		"""
		In: Absolute Unix path
		Out: Absolute Wine path
		"""

		if len(in_path) > MAX_PATH:
			raise # TODO

		in_path_astr_p = ctypes.pointer(self.__str_to_winastr__(in_path))
		out_path_ustr_p = ctypes.pointer(UNICODE_STRING())

		ntstatus = self.__unix_to_wine__(
			in_path_astr_p, out_path_ustr_p
			)

		if ntstatus != 0:
			raise # TODO

		out_path = self.__winustr_to_str__(out_path_ustr_p.contents)

		# https://github.com/wine-mirror/wine/blob/07cf14dc928a1a00baecbbc7ca5a6f3fe680238c/dlls/kernel32/path.c#L1955
		if out_path[5] == ':':
			return out_path[4:]
		else:
			out_path[1] = '\\'
			return out_path


	def wine_to_unix(self, in_path):
		"""
		In: Absolute Wine path
		Out: Absolute Unix path
		"""

		if len(in_path) > MAX_PATH:
			raise # TODO

		in_path_buffer_p = ctypes.pointer(ctypes.create_unicode_buffer(in_path + '\0'))
		in_path_ustr_p = ctypes.pointer(UNICODE_STRING())

		self.__dos_to_nt__(in_path_buffer_p, in_path_ustr_p, None, None)

		out_path_astr_p = ctypes.pointer(ANSI_STRING())

		ntstatus = self.__wine_to_unix__(
			in_path_ustr_p, out_path_astr_p,
			self.FILE_OPEN_IF, int(False)
			)

		if ntstatus != 0:
			raise # TODO

		return self.__winastr_to_str__(out_path_astr_p.contents)


	def __str_to_winastr__(self, in_str_u):
		"""
		In: Python unicode string
		Out: ANSI_STRING
		"""

		in_str_a = in_str_u.encode('utf-8')
		in_astr = ANSI_STRING()
		in_astr.Length = len(in_str_a)
		in_astr.MaximumLength = len(in_str_a) + 2
		in_astr.Buffer = wintypes.LPSTR(in_str_a)

		return in_astr


	def __str_to_winustr__(self, in_str_u):
		"""
		In: Python unicode string
		Out: UNICODE_STRING
		"""

		in_ustr = UNICODE_STRING()
		in_ustr.Length = len(in_str_u)
		in_ustr.MaximumLength = len(in_str_u) + 2
		in_ustr.Buffer = wintypes.LPWSTR(in_str_u)

		return in_ustr


	def __winastr_to_str__(self, in_astr):
		"""
		In: ANSI_STRING
		Out: Python unicode string
		"""

		return in_astr.Buffer.decode('utf-8')


	def __winustr_to_str__(self, in_ustr):
		"""
		In: UNICODE_STRING
		Out: Python unicode string
		"""

		return in_ustr.Buffer
