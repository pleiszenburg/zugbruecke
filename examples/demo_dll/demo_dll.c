#include "demo_dll.h"

void __stdcall DEMOROUTINE_DUMP demo_routine(
	char *ch_str1,
	int ch_lenstr1,
	char *ch_str2, 
	int ch_lenstr2,
	struct L1 *Log1,
	struct C1 *Str1,
	struct I1 *Int1,
	struct R1 *Real1,
	struct ResC *Resultc,
	struct ResV *Resultv
	)
{
	
	FILE *fd_ch_str1;
	fd_ch_str1 = fopen("dump_ch_str1.bin","wb");
	fwrite(ch_str1, sizeof(*ch_str1), 1, fd_ch_str1);
	fclose(fd_ch_str1);
	
	FILE *fd_ch_str2;
	fd_ch_str2 = fopen("dump_ch_str2.bin","wb");
	fwrite(ch_str2, sizeof(*ch_str2), 1, fd_ch_str2);
	fclose(fd_ch_str2);
	
	FILE *fd_log1;
	fd_log1 = fopen("dump_log1.bin","wb");
	fwrite(Log1, sizeof(*Log1), 1, fd_log1);
	fclose(fd_log1);
	
	FILE *fd_str1;
	fd_str1 = fopen("dump_str1.bin","wb");
	fwrite(Str1, sizeof(*Str1), 1, fd_str1);
	fclose(fd_str1);
	
	FILE *fd_int1;
	fd_int1 = fopen("dump_int1.bin","wb");
	fwrite(Int1, sizeof(*Int1), 1, fd_int1);
	fclose(fd_int1);
	
	FILE *fd_real1;
	fd_real1 = fopen("dump_real1.bin","wb");
	fwrite(Real1, sizeof(*Real1), 1, fd_real1);
	fclose(fd_real1);
	
	FILE *fd_resultc;
	fd_resultc = fopen("dump_resultc.bin","wb");
	fwrite(Resultc, sizeof(*Resultc), 1, fd_resultc);
	fclose(fd_resultc);
	
	FILE *fd_resultv;
	fd_resultv = fopen("dump_resultv.bin","wb");
	fwrite(Resultv, sizeof(*Resultv), 1, fd_resultv);
	fclose(fd_resultv);
	
	FILE *fd_log1_a;
	fd_log1_a = fopen("dump_log1.txt","w");
	fprintf(fd_log1_a, "Depart = '%d' \n", (*Log1).Depart);
	fprintf(fd_log1_a, "Flyby = '%d' \n", (*Log1).Flyby);
	fprintf(fd_log1_a, "Jetis = '%d' \n", (*Log1).Jetis);
	fprintf(fd_log1_a, "Jetisd = '%d' \n", (*Log1).Jetisd);
	fprintf(fd_log1_a, "Keep = '%d' \n", (*Log1).Keep);
	fprintf(fd_log1_a, "Printanom = '%d' \n", (*Log1).Printanom);
	fprintf(fd_log1_a, "Retro = '%d' \n", (*Log1).Retro);
	fprintf(fd_log1_a, "Write_output = '%d' \n", (*Log1).Write_output);
	fprintf(fd_log1_a, "Zero = '%d' \n", (*Log1).Zero);
	fprintf(fd_log1_a, "Dump[0] = '%d' \n", (*Log1).Dump[0]);
	fprintf(fd_log1_a, "Dump[1] = '%d' \n", (*Log1).Dump[1]);
	fprintf(fd_log1_a, "Dump[2] = '%d' \n", (*Log1).Dump[2]);
	fprintf(fd_log1_a, "Dump[3] = '%d' \n", (*Log1).Dump[3]);
	fclose(fd_log1_a);
	
	FILE *fd_int1_a;
	fd_int1_a = fopen("dump_int1.txt","w");
	fprintf(fd_int1_a, "Choice = '%d' \n", (*Int1).Choice);
	fprintf(fd_int1_a, "Ia = '%d' \n", (*Int1).Ia);
	fprintf(fd_int1_a, "Icb = '%d' \n", (*Int1).Icb);
	fprintf(fd_int1_a, "Il = '%d' \n", (*Int1).Il);
	fprintf(fd_int1_a, "Iname = '%d' \n", (*Int1).Iname);
	fprintf(fd_int1_a, "Iprnt = '%d' \n", (*Int1).Iprnt);
	fprintf(fd_int1_a, "Itmax = '%d' \n", (*Int1).Itmax);
	fprintf(fd_int1_a, "Mjet = '%d' \n", (*Int1).Mjet);
	fprintf(fd_int1_a, "Nb1 = '%d' \n", (*Int1).Nb1);
	fprintf(fd_int1_a, "Nb1 = '%d' \n", (*Int1).Nb2);
	fprintf(fd_int1_a, "Ncop = '%d' \n", (*Int1).Ncop);
	fprintf(fd_int1_a, "Nctopy = '%d' \n", (*Int1).Nctopy);
	fprintf(fd_int1_a, "Nlv = '%d' \n", (*Int1).Nlv);
	fprintf(fd_int1_a, "Nmuop = '%d' \n", (*Int1).Nmuop);
	fprintf(fd_int1_a, "Nout = '%d' \n", (*Int1).Nout);
	fprintf(fd_int1_a, "Npow = '%d' \n", (*Int1).Npow);
	fprintf(fd_int1_a, "Nsr = '%d' \n", (*Int1).Nsr);
	fprintf(fd_int1_a, "Nt = '%d' \n", (*Int1).Nt);
	fprintf(fd_int1_a, "Nv1 = '%d' \n", (*Int1).Nv1);
	fprintf(fd_int1_a, "Nv2 = '%d' \n", (*Int1).Nv2);
	fprintf(fd_int1_a, "Eopt[0] = '%d' \n", (*Int1).Eopt[0]);
	fprintf(fd_int1_a, "Eopt[1] = '%d' \n", (*Int1).Eopt[1]);
	fprintf(fd_int1_a, "Ic[0] = '%d' \n", (*Int1).Ic[0]);
	fprintf(fd_int1_a, "Ic[1] = '%d' \n", (*Int1).Ic[1]);
	fprintf(fd_int1_a, "Ip[0] = '%d' \n", (*Int1).Ip[0]);
	fprintf(fd_int1_a, "Ip[1] = '%d' \n", (*Int1).Ip[1]);
	fprintf(fd_int1_a, "Iu[0] = '%d' \n", (*Int1).Iu[0]);
	fprintf(fd_int1_a, "Iu[1] = '%d' \n", (*Int1).Iu[1]);
	fprintf(fd_int1_a, "Jdl[0] = '%d' \n", (*Int1).Jdl[0]);
	fprintf(fd_int1_a, "Jdl[1] = '%d' \n", (*Int1).Jdl[1]);
	fprintf(fd_int1_a, "Jdl[2] = '%d' \n", (*Int1).Jdl[2]);
	fprintf(fd_int1_a, "Jdl[3] = '%d' \n", (*Int1).Jdl[3]);
	fprintf(fd_int1_a, "Jdl[4] = '%d' \n", (*Int1).Jdl[4]);
	fprintf(fd_int1_a, "Jdl[5] = '%d' \n", (*Int1).Jdl[5]);
	fprintf(fd_int1_a, "Nflag[0] = '%d' \n", (*Int1).Nflag[0]);
	fprintf(fd_int1_a, "Nflag[1] = '%d' \n", (*Int1).Nflag[1]);
	fclose(fd_int1_a);
	
        printf("Dump!\n");
	
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
