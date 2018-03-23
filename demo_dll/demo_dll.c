/*

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	demo_dll/demo_dll.c: Routines for testing ctypes interface

	Required to run on platform / side: [WINE]

	Copyright (C) 2017-2018 Sebastian M. Ernst <ernst@pleiszenburg.de>

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


/* Function involving a C data structure - returning a pointer to a variable */
double __stdcall DEMODLL *cookbook_distance_pointer(
	cookbook_point *p1,
	cookbook_point *p2
	)
{
	double *distance_p = (double *)malloc(sizeof(double));
	*distance_p = hypot(p1->x - p2->x, p1->y - p2->y);
	return distance_p;
}


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// zugbruecke demo
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

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


void __stdcall DEMODLL bubblesort_struct(
	bubblesort_data *data
	)
{
	int i, j;
	for (i = 0; i < data->n - 1; ++i)
	{
		for (j = 0; j < data->n - i - 1; ++j)
		{
			if (data->a[j] > data->a[j + 1])
			{
				float tmp = data->a[j];
				data->a[j] = data->a[j + 1];
				data->a[j + 1] = tmp;
			}
		}
	}
}


void __stdcall DEMODLL bubblesort_segments(
	float *a,
	int number_of_segments,
	int elements_per_segment
	)
{
	int i, j;
	int n = number_of_segments * elements_per_segment;
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


void __stdcall DEMODLL mix_rgb_colors(
	int8_t color_a[3],
	int8_t color_b[3],
	int8_t *color_mixed
	)
{
	int i;
	for (i = 0; i < 3; i++)
	{
		color_mixed[i] = (color_a[i] + color_b[i]) / 2;
	}
}


void __stdcall DEMODLL gauss_elimination(
	float (*A)[3][4],
	float (*x)[3]
	)
{

	int i, j, k, n = 3;
	float c, sum = 0.0;

	for(j = 0; j < n; j++)
	{
		for(i = j + 1; i < n; i++)
		{
			c = (*A)[i][j] / (*A)[j][j];
			for(k = 0; k <= n; k++)
			{
				(*A)[i][k] = (*A)[i][k] - c * (*A)[j][k];
			}
		}
	}

	(*x)[n - 1] = (*A)[n - 1][n] / (*A)[n - 1][n - 1];

	for(i = n - 2; i >= 0; i--)
	{
		sum = 0;
		for(j = i + 1; j < n; j++)
		{
			sum = sum + (*A)[i][j] * (*x)[j];
		}
		(*x)[i] = ((*A)[i][n] - sum) / (*A)[i][i];
	}

}


vector3d __stdcall DEMODLL *vector3d_add(
	vector3d *v1,
	vector3d *v2
	)
{

	vector3d *v3 = malloc(sizeof(vector3d));

	v3->x = v1->x + v2->x;
	v3->y = v1->y + v2->y;
	v3->z = v1->z + v2->z;

	return v3;

}


int16_t __stdcall DEMODLL sqrt_int(
	int16_t a
	)
{
	return sqrt(a);
}


int16_t __stdcall DEMODLL square_int(
	int16_t a
	)
{
	return a * a;
}


int16_t __stdcall DEMODLL add_ints(
	int16_t a,
	int16_t b
	)
{
	return a + b;
}


float __stdcall DEMODLL add_floats(
	float a,
	float b
	)
{
	return a + b;
}


int16_t __stdcall DEMODLL subtract_ints(
	int16_t a,
	int16_t b
	)
{
	return a - b;
}


int16_t __stdcall DEMODLL pow_ints(
	int16_t a,
	int16_t b
	)
{
	return pow(a, b);
}


int16_t __stdcall DEMODLL get_const_int(void)
{
	return sqrt(49);
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

	int8_t i, j;

	for(i = 0; i < 4; i++)
	{
		(*param_struct_test_p).el_int8t_4[i] *= i;
	}

	for(i = 0; i < 3; i++)
	{
		for(j = 0; j < 2; j++)
		{
			(*param_struct_test_p).el_int8t_2x3[i][j] += i + j;
		}
	}

}


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// zugbruecke demo: callback
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

int16_t __stdcall DEMODLL sum_elements_from_callback(
	int16_t len,
	conveyor_belt get_data
	)
{

	int16_t sum = 0;
	int16_t i;

	for(i = 0; i < len; i++)
	{
		sum += get_data(i);
	}

	return sum;

}


int16_t __stdcall DEMODLL sum_elements_from_callback_in_struct(
	struct conveyor_belt_data *data
	)
{

	int16_t sum = 0;
	int16_t i;

	for(i = 0; i < data->len; i++)
	{
		sum += data->get_data(i);
	}

	return sum;

}


int16_t __stdcall DEMODLL use_optional_callback_a(
	int16_t in_data,
	conveyor_belt process_data
	)
{
	int16_t tmp;
	if(process_data) {
		tmp = process_data(in_data);
	} else {
		tmp = in_data;
	}
	return tmp * 2;
}


int16_t __stdcall DEMODLL use_optional_callback_b(
	int16_t in_data,
	conveyor_belt process_data
	)
{
	int16_t tmp;
	if(process_data) {
		tmp = process_data(in_data);
	} else {
		tmp = in_data;
	}
	return tmp * 2;
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
