/*

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	demo_dll/demo_dll.c: Routines for testing ctypes interface

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


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// INCLUDE
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#include "demo_dll.h"


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// Python Cookbook R3 Demo: https://github.com/dabeaz/python-cookbook/blob/master/src/15/sample.c
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

/* Compute the greatest common divisor */
int __stdcall DEMODLL cookbook_gcd(
	int x,
	int y
	)
{
	int g = y;
	while (x > 0)
	{
		g = x;
		x = y % x;
		y = g;
	}
	return g;
}


/* Test if (x0,y0) is in the Mandelbrot set or not */
int __stdcall DEMODLL cookbook_in_mandel(
	double x0,
	double y0,
	int n
	)
{
	double x = 0, y = 0, xtemp;
	while (n > 0)
	{
		xtemp = x * x - y * y + x0;
		y = 2 * x * y + y0;
		x = xtemp;
		n -= 1;
		if (x * x + y * y > 4) return 0;
	}
	return 1;
}


/* Divide two numbers */
int __stdcall DEMODLL cookbook_divide(
	int a,
	int b,
	int *remainder
	)
{
	int quot = a / b;
	*remainder = a % b;
	return quot;
}


/* Average values in an array */
double __stdcall DEMODLL cookbook_avg(
	double *a,
	int n
	)
{
	int i;
	double total = 0.0;
	for (i = 0; i < n; i++)
	{
		total += a[i];
	}
	return total / n;
}


/* Function involving a C data structure */
double __stdcall DEMODLL cookbook_distance(
	cookbook_point *p1,
	cookbook_point *p2
	)
{
	return hypot(p1->x - p2->x, p1->y - p2->y);
}


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// zugbruecke demo
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

/* Average values in an array */
void __stdcall DEMODLL bubblesort(
	float *a,
	int n
	)
{
	int i, j;
	for (i = 0; i < n - 1; ++i)
	{
		for (j = 0; j < n - i - 1; ++j)
		{
			if (a[j] > a[j + 1])
			{
				float tmp = a[j];
				a[j] = a[j + 1];
				a[j + 1] = tmp;
			}
		}
	}
}


float __stdcall DEMODLL simple_demo_routine(
	float param_a,
	float param_b
	)
{
	return param_a - (param_a / param_b);
}


void __stdcall DEMODLL complex_demo_routine(
	char *param_char_p,
	int param_int,
	struct test *param_struct_test_p
	)
{
	printf("el_int8t = '%d' \n", (*param_struct_test_p).el_int8t);
	printf("el_int8t_4[0] = '%d' \n", (*param_struct_test_p).el_int8t_4[0]);
	printf("el_int8t_4[1] = '%d' \n", (*param_struct_test_p).el_int8t_4[1]);
	printf("el_int8t_4[2] = '%d' \n", (*param_struct_test_p).el_int8t_4[2]);
	printf("el_int8t_4[3] = '%d' \n", (*param_struct_test_p).el_int8t_4[3]);
}


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// DLL infrastructure
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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
