/*

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	demo_dll/demo_dll.h: DLL header

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

*/

#ifndef DEMODLL_H
#define DEMODLL_H


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// INCLUDE
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#include <stdio.h>
#include <windows.h>
#include <stdint.h>
#include <math.h>


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// MACROS
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

// #ifdef BUILDING_EXAMPLE_DLL
// #define DEMODLL __declspec(dllexport)
// #else
#define DEMODLL __declspec(dllimport)
// #endif

typedef int32_t bool;
#define TRUE 1
#define FALSE 0


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// Python Cookbook R3 Demo: https://github.com/dabeaz/python-cookbook/blob/master/src/15/sample.c
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

int __stdcall DEMODLL cookbook_gcd(
	int x,
	int y
	);

int __stdcall DEMODLL cookbook_in_mandel(
	double x0,
	double y0,
	int n
	);

int __stdcall DEMODLL cookbook_divide(
	int a,
	int b,
	int *remainder
	);

double __stdcall DEMODLL cookbook_avg(
	double *a,
	int n
	);

typedef struct cookbook_point {
	double x, y;
} cookbook_point;

double __stdcall DEMODLL cookbook_distance(
	cookbook_point *p1,
	cookbook_point *p2
	);


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// zugbruecke demo
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

void __stdcall DEMODLL bubblesort(
	float *a,
	int n
	);

void __stdcall DEMODLL mix_rgb_colors(
	int8_t color_a[3],
	int8_t color_b[3],
	int8_t *color_mixed
	);

void __stdcall DEMODLL gauss_elimination(
	float (*A)[3][4],
	float (*x)[3]
	);

typedef struct vector3d {
	el_int16t x, y, z;
} vector3d;

vector3d __stdcall DEMODLL *vector3d_add(
	vector3d *p1,
	vector3d *p2
	);

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


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// DLL infrastructure
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

DEMODLL bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved);

// DEMODLL_H
#endif
