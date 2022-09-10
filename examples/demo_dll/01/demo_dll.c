/*

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

	demo_dll/01/demo_dll.c: Routines for testing ctypes interface

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


vector3d __stdcall DEMODLL *vector3d_add_array(
	vector3d *v,
	int16_t len
	)
{

	int16_t i;

	vector3d *v_out = malloc(sizeof(vector3d));
	v_out->x = 0;
	v_out->y = 0;
	v_out->z = 0;

	for(i = 0; i < len; i++)
	{
		v_out->x += v[i].x;
		v_out->y += v[i].y;
		v_out->z += v[i].z;
	}

	return v_out;

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


int16_t __stdcall DEMODLL mul_ints(
	int16_t a,
	int16_t b
	)
{
	return a * b;
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


int16_t __stdcall DEMODLL sub_ints(
	int16_t a,
	int16_t b
	)
{
	return a - b;
}


int16_t __stdcall DEMODLL get_const_int(void)
{
	return sqrt(49);
}


void __stdcall DEMODLL square_int_array(
	int16_t *in_array,
	void *out_array,
	int16_t len
	)
{
	int i;
	int16_t **out_array_p = out_array;
	*out_array_p = malloc(sizeof(int16_t) * len);
	for(i = 0; i < len; i++)
	{
		(*out_array_p)[i] = in_array[i] * in_array[i];
	}
}


void __stdcall DEMODLL square_int_array_with_struct(
	int_array_data *in_array,
	int_array_data *out_array
	)
{
	int i;
	out_array->len = in_array->len;
	out_array->data = malloc(sizeof(int16_t) * out_array->len);
	for(i = 0; i < in_array->len; i++)
	{
		out_array->data[i] = in_array->data[i] * in_array->data[i];
	}
}


int_array_data __stdcall DEMODLL *fibonacci_sequence_a(
	int16_t len
	)
{
	int16_t i;
	int_array_data *out_data = malloc(sizeof(int_array_data));
	out_data->len = len;
	out_data->data = malloc(sizeof(int16_t) * out_data->len);
	for(i = 0; i < len; i++){
		if(i == 0 || i == 1) { out_data->data[i] = 1; continue; }
		out_data->data[i] = out_data->data[i - 1] + out_data->data[i - 2];
	}
	return out_data;
}


void __stdcall DEMODLL replace_letter_in_null_terminated_string_a(
	char *in_string,
	char old_letter,
	char new_letter
	)
{
	int i;
	for (i = 0; i < strlen(in_string); i++) {
		if(in_string[i] == old_letter) {
			in_string[i] = new_letter;
		}
	}
}


void __stdcall DEMODLL replace_letter_in_null_terminated_string_b(
	char *in_string,
	char old_letter,
	char new_letter
	)
{
	int i;
	for (i = 0; i < strlen(in_string); i++) {
		if(in_string[i] == old_letter) {
			in_string[i] = new_letter;
		}
	}
}


void __stdcall DEMODLL replace_letter_in_null_terminated_string_unicode_a(
	wchar_t *in_string,
	wchar_t old_letter,
	wchar_t new_letter
	)
{
	int i;
	for (i = 0; i < wcslen(in_string); i++) {
		if(in_string[i] == old_letter) {
			in_string[i] = new_letter;
		}
	}
}


void __stdcall DEMODLL replace_letter_in_null_terminated_string_unicode_b(
	wchar_t *in_string,
	wchar_t old_letter,
	wchar_t new_letter
	)
{
	int i;
	for (i = 0; i < wcslen(in_string); i++) {
		if(in_string[i] == old_letter) {
			in_string[i] = new_letter;
		}
	}
}


void __stdcall DEMODLL replace_letter_in_null_terminated_string_r(
	char **in_string,
	char old_letter,
	char new_letter
	)
{
	int i;
	for (i = 0; i < strlen((*in_string)); i++) {
		if((*in_string)[i] == old_letter) {
			(*in_string)[i] = new_letter;
		}
	}
}


void __stdcall DEMODLL tag_string_a(
	char *in_string,
	void *out_string
	)
{
	int str_len = strlen(in_string);

	char **out_string_p = out_string;
	*out_string_p = malloc(sizeof(char) * (str_len + 2));
	strncpy((*out_string_p) + 1, in_string, str_len);
	(*out_string_p)[0] = '<';
	(*out_string_p)[str_len + 1] = '>';
	(*out_string_p)[str_len + 2] = '\0';
}


void __stdcall DEMODLL tag_string_b(
	char *in_string,
	void *out_string
	)
{
	int str_len = strlen(in_string);

	char **out_string_p = out_string;
	*out_string_p = malloc(sizeof(char) * (str_len + 2));
	strncpy((*out_string_p) + 1, in_string, str_len);
	(*out_string_p)[0] = '<';
	(*out_string_p)[str_len + 1] = '>';
	(*out_string_p)[str_len + 2] = '\0';
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


int16_t _coordinates_in_image_(
	image_data *in_image, int16_t x, int16_t y
	)
{
	if(x < 0 || x >= in_image->width || y < 0 || y >= in_image->height){ return 0; }
	return 1;
}


int16_t _image_pixel_get_(
	image_data *in_image, int16_t x, int16_t y
	)
{
	if(!_coordinates_in_image_(in_image, x, y)) { return 0; }
	return in_image->data[(in_image->width * y) + x];
}


void _image_pixel_set_(
	image_data *in_image, int16_t x, int16_t y, int16_t value
	)
{
	if(!_coordinates_in_image_(in_image, x, y)) { return; }
	in_image->data[(in_image->width * y) + x] = value;
}


void _image_copy_segment_to_buffer_(
	image_data *in_image, image_data *in_buffer, int16_t x, int16_t y
	)
{
	int16_t m, n;
	for(m = 0; m < in_buffer->width; m++)
	{
		for(n = 0; n < in_buffer->height; n++)
		{
			_image_pixel_set_(in_buffer, m, n, _image_pixel_get_(in_image, x + m, y + n));
		}
	}
}


void __stdcall DEMODLL apply_filter_to_image(
	image_data *in_image,
	image_data *out_image,
	filter_func_type filter_func
	)
{

	int16_t i, j;
	const int16_t F_W = 3;
	const int16_t F_H = 3;
	const int16_t F_W_off = F_W / 2;
	const int16_t F_H_off = F_H / 2;

	out_image->data = malloc(sizeof(int16_t) * in_image->width * in_image->height);
	out_image->width = in_image->width;
	out_image->height = in_image->height;

	image_data *buffer = malloc(sizeof(image_data));
	buffer->data = malloc(sizeof(int16_t) * F_W * F_H);
	buffer->width = F_W;
	buffer->height = F_H;

	for(i = 0; i < in_image->width; i++)
	{
		for(j = 0; j < in_image->height; j++)
		{
			_image_copy_segment_to_buffer_(in_image, buffer, i - F_W_off, j - F_H_off);
			_image_pixel_set_(out_image, i, j, filter_func(buffer));
		}
	}

	free(buffer->data);
	free(buffer);

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
