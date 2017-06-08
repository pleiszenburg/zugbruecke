#ifndef DEMOROUTINE_DUMP_H
#define DEMOROUTINE_DUMP_H

#include <stdio.h>
#include <windows.h>
#include <stdint.h>

// #ifdef BUILDING_EXAMPLE_DLL
// #define DEMOROUTINE_DUMP __declspec(dllexport)
// #else
#define DEMOROUTINE_DUMP __declspec(dllimport)
// #endif

typedef int32_t bool;
#define TRUE  1
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

float __stdcall DEMOROUTINE_DUMP simple_demo_routine(
	float param_a,
	float param_b
	);

void __stdcall DEMOROUTINE_DUMP complex_demo_routine(
	char *param_char_p,
	int param_int,
	struct test *param_struct_test_p
	);

DEMOROUTINE_DUMP bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved);

#endif
