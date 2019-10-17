
WINDLL_HEADER = """

#ifndef TESTDLL_H
#define TESTDLL_H

#include <stdio.h>
#include <windows.h>
#include <stdint.h>
#include <math.h>

#define DEMODLL __declspec(dllimport)

typedef int32_t bool;
#define TRUE 1
#define FALSE 0

{{ HEADER }}

DEMODLL bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved);

#endif

"""

WINDLL_SOURCE = """

#include "{{ HEADER_FN }}"

{{ SOURCE }}

DEMODLL bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
		break;
	case DLL_THREAD_ATTACH:
		break;
	case DLL_THREAD_DETACH:
		break;
	case DLL_PROCESS_DETACH:
		break;
	}
	return TRUE;
}

"""

CC = {
	'win32': 'i686-w64-mingw32-gcc',
	'win64': 'x86_64-w64-mingw32-gcc',
	}
CFLAGS = [
	'-Wall',
	'-Wl,-add-stdcall-alias',
	'-shared',
	'-std=c99'
	]
LDFLAGS = [
	'-lm',
	]
