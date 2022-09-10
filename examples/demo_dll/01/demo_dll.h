/*

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	demo_dll/01/demo_dll.h: DLL header

	Required to run on platform / side: [WINE]

	Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

double __stdcall DEMODLL *cookbook_distance_pointer(
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

typedef struct bubblesort_data {
	float *a;
	int n;
} bubblesort_data;

void __stdcall DEMODLL bubblesort_struct(
	bubblesort_data *data
	);

void __stdcall DEMODLL bubblesort_segments(
	float *a,
	int number_of_segments,
	int elements_per_segment
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
	int16_t x, y, z;
} vector3d;

vector3d __stdcall DEMODLL *vector3d_add(
	vector3d *p1,
	vector3d *p2
	);

vector3d __stdcall DEMODLL *vector3d_add_array(
	vector3d *v,
	int16_t len
	);

int16_t __stdcall DEMODLL sqrt_int(
	int16_t a
	);

int16_t __stdcall DEMODLL square_int(
	int16_t a
	);

int16_t __stdcall DEMODLL add_ints(
	int16_t a,
	int16_t b
	);

int16_t __stdcall DEMODLL mul_ints(
	int16_t a,
	int16_t b
	);

float __stdcall DEMODLL add_floats(
	float a,
	float b
	);

int16_t __stdcall DEMODLL subtract_ints(
	int16_t a,
	int16_t b
	);

int16_t __stdcall DEMODLL pow_ints(
	int16_t a,
	int16_t b
	);

int16_t __stdcall DEMODLL sub_ints(
	int16_t a,
	int16_t b
	);

int16_t __stdcall DEMODLL get_const_int(void);

void __stdcall DEMODLL square_int_array(
	int16_t *in_array,
	void *out_array,
	int16_t len
	);

typedef struct int_array_data {
	int16_t *data;
	int16_t len;
} int_array_data;

void __stdcall DEMODLL square_int_array_with_struct(
	int_array_data *in_array,
	int_array_data *out_array
	);

int_array_data __stdcall DEMODLL *fibonacci_sequence_a(
	int16_t len
	);

void __stdcall DEMODLL replace_letter_in_null_terminated_string_a(
	char *in_string,
	char old_letter,
	char new_letter
	);

void __stdcall DEMODLL replace_letter_in_null_terminated_string_b(
	char *in_string,
	char old_letter,
	char new_letter
	);

void __stdcall DEMODLL replace_letter_in_null_terminated_string_r(
	char **in_string,
	char old_letter,
	char new_letter
	);

void __stdcall DEMODLL replace_letter_in_null_terminated_string_unicode_a(
	wchar_t *in_string,
	wchar_t old_letter,
	wchar_t new_letter
	);

void __stdcall DEMODLL replace_letter_in_null_terminated_string_unicode_b(
	wchar_t *in_string,
	wchar_t old_letter,
	wchar_t new_letter
	);

void __stdcall DEMODLL tag_string_a(
	char *in_string,
	void *out_string
	);

void __stdcall DEMODLL tag_string_b(
	char *in_string,
	void *out_string
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
// zugbruecke demo: callback
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

typedef int16_t __stdcall (*conveyor_belt)(int16_t index);

int16_t __stdcall DEMODLL sum_elements_from_callback(
	int16_t len,
	conveyor_belt get_data
	);

typedef struct conveyor_belt_data {
	int16_t len;
	conveyor_belt get_data;
} conveyor_belt_data;

int16_t __stdcall DEMODLL sum_elements_from_callback_in_struct(
	struct conveyor_belt_data *data
	);

typedef struct image_data {
	int16_t *data;
	int16_t width;
	int16_t height;
} image_data;

typedef int16_t __stdcall (*filter_func_type)(image_data *section);

void __stdcall DEMODLL apply_filter_to_image(
	image_data *in_image,
	image_data *out_image,
	filter_func_type filter_func
	);

int16_t __stdcall DEMODLL use_optional_callback_a(
	int16_t in_data,
	conveyor_belt process_data
	);

int16_t __stdcall DEMODLL use_optional_callback_b(
	int16_t in_data,
	conveyor_belt process_data
	);


// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
// DLL infrastructure
// +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

DEMODLL bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved);

// DEMODLL_H
#endif
