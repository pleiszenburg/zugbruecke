#include "demo_dll.h"

void __stdcall DEMOROUTINE_DUMP demo_routine(
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
