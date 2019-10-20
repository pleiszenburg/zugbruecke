
DLL_HEADER = """

#ifndef TESTDLL_H
#define TESTDLL_H

#include <stdio.h>
#include <windows.h>
#include <stdint.h>
#include <math.h>

typedef int32_t bool;
#define TRUE 1
#define FALSE 0

{{ HEADER }}

#endif

"""

DLL_SOURCE = """

#include "{{ HEADER_FN }}"

{{ SOURCE }}

"""

ARCHS = ['win32', 'win64']
CONVENTIONS = ['cdll', 'windll']

PREFIX = {
	'cdll': '__declspec(dllexport)',
	'windll': '__declspec(dllexport)',
	}
SUFFIX = {
	'cdll': '__cdecl',
	'windll': '__stdcall',
	}

CC = {
	'win32': 'i686-w64-mingw32-gcc',
	'win64': 'x86_64-w64-mingw32-gcc',
	}
_CFLAGS = [
	'-Wall',
	'-shared',
	'-std=c99'
	]
CFLAGS = {
	'cdll': _CFLAGS + ['-Wl,--subsystem,windows'],
	'windll': _CFLAGS + ['-Wl,-add-stdcall-alias'],
	}
LDFLAGS = [
	'-lm',
	]
