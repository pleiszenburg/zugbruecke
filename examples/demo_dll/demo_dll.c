/*

PYCROSSCALL
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/s-m-e/pycrosscall

	examples/demo_dll/demo_dll.c: Routines for testing ctypes interface

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


#include "demo_dll.h"

float __stdcall DEMOROUTINE_DUMP simple_demo_routine(
	float param_a,
	float param_b
	)
{

	return param_a - (param_a / param_b);

}

void __stdcall DEMOROUTINE_DUMP complex_demo_routine(
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

DEMOROUTINE_DUMP bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
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
