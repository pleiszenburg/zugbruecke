/*

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	examples/demo_dll/demo_dll.h: DLL header

	Required to run on platform / side: [WINE]

	Copyright (C) 2017 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/s-m-e/pycrosscall/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

*/


#ifndef DEMODLL_H
#define DEMODLL_H

#include <stdio.h>
#include <windows.h>
#include <stdint.h>

// #ifdef BUILDING_EXAMPLE_DLL
// #define DEMODLL __declspec(dllexport)
// #else
#define DEMODLL __declspec(dllimport)
// #endif

typedef int32_t bool;
#define TRUE 1
#define FALSE 0

struct test
{
	char el_char;
	int8_t el_int8t;
	int16_t el_int16t;
	float el_float;
	double el_double;
	int8_t el_int8t_4[4];
	int8_t el_int8t_2x3[2][3];
};

float __stdcall DEMODLL simple_demo_routine(
	float param_a,
	float param_b
	);

void __stdcall DEMODLL complex_demo_routine(
	char *param_char_p,
	int param_int,
	struct test *param_struct_test_p
	);

DEMODLL bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved);

// DEMODLL_H
#endif
