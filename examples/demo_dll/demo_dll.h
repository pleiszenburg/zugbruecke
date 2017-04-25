#ifndef DEMOROUTINE_DUMP_H
#define DEMOROUTINE_DUMP_H

#include <stdio.h>
#include <windows.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// #ifdef BUILDING_EXAMPLE_DLL
// #define DEMOROUTINE_DUMP __declspec(dllexport)
// #else
#define DEMOROUTINE_DUMP __declspec(dllimport)
// #endif

typedef int32_t bool;
#define TRUE  1
#define FALSE 0

struct L1
{
	int8_t Depart;
	int8_t Flyby;
	int8_t Jetis;
	int8_t Jetisd;
	int8_t Keep;
	int8_t Printanom;
	int8_t Retro;
	int8_t Write_output;
	int8_t Zero;
	int8_t Dump[4]; // (3)
};

struct C1
{
	char Acpath[48]; // As String * 48
	char Sarray[8]; // As String * 8
	char Bulsi[8]; //  As String * 8
	char Head[120]; // As String * 120
	char Ptype[1]; //  As String * 1
	char Acname[4][12]; // (3) As String * 12
	char Shota[4][8]; // (3) As String * 8
};

struct I1
{
	int16_t Choice;
	int16_t Ia;
	int16_t Icb;
	int16_t Il;
	int16_t Iname;
	int16_t Iprnt;
	int16_t Itmax;
	int16_t Mjet;
	int16_t Nb1;
	int16_t Nb2;
	int16_t Ncop;
	int16_t Nctopy;
	int16_t Nlv;
	int16_t Nmuop;
	int16_t Nout;
	int16_t Npow;
	int16_t Nsr;
	int16_t Nt;
	int16_t Nv1;
	int16_t Nv2;
	int16_t Eopt[2]; // (1)
	int16_t Ic[2]; // (1)
	int16_t Ip[2]; // (1)
	int16_t Iu[2]; // (1)
	int16_t Jdl[6]; // (5)
	int16_t Nflag[2]; // (1)
};

struct R1
{

	double Accelflg;
	double Acf;
	double Alt;
	double Alta;
	double Altv;
	double Bb;
	double Cisp;
	double Contin;
	double Dd;
	double Delpo;
	double Epoch;
	double Fxdmassd;
	double Ispd;
	double Glossd;
	double Kadp;
	double Ks;
	double Kt;
	double Ktd;
	double Lvcont;
	double M0;
	double M0d;
	double Madp;
	double Pmin;
	double Ptilt;
	double Ra;
	double Radep;
	double Rarr;
	double Rarv;
	double Rdep;
	double Rn;
	double Rp;
	double Rparr;
	double Rpdep;
	double Rpe;
	double Rtilt;
	double Sap;
	double T0;
	double Tstay;
	double Alfa[2]; // (1) 
	double Gmp[2]; // (1) 
	double Kd[2]; // (1) 
	double Kr[2]; // (1) 
	double Rpl[2]; // (1) 
	double P0[3]; // (2) 
	double Adate[3]; // (2) 
	double Is_r[3]; // (2) 
	double Isp[3]; // (2) 
	double Jdate[3]; // (2) 
	double Tend[3]; // (2) 
	double V1[3]; // (2) 
	double V2[3]; // (2) 
	double Vhl[3]; // (2) 
	double Vhp[3]; // (2) 
	double Mlv[4]; // (3) 
	double Gamap[5]; // (4) 
	double Pcons[5]; // (4) 
	double Orb1[6]; // (5) 
	double Orb2[6]; // (5) 
	double Xa[12]; // (11) 
	double Xl[12]; // (11) 
};

struct ResC
{
	char Bca[12]; // As String * 12
	char Bcl[12]; // As String * 12
	char Bodies[2][30]; // (1 To 2) As String * 30
	char Bcd[37][6]; // (1 To 37) As String * 6
	char str0n[30][4]; // (1 To 30) As String * 4
	char strLine[3][132]; // (1 To 3) As String * 132
	char strUn[2][2]; // (1 To 2) As String * 2
};

struct ResV
{
	double Date[2]; // (1 To 2);
	double Vel1;
	double Vel2;
	double Ps;
	double Data[11][35]; // (1 To 11, 1 To 35)
	double Pr[37]; // (36)
	double OnValues[30]; // (1 To 30)
	double Time[2]; // (1 To 2)
	double M0[2]; // (1 To 2);
	double M[2]; // (1 To 2); HACK: was "M"
	double Mp[2]; // (1 To 2);
	int16_t Max;
	int16_t NoOn;
};

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
	);

DEMOROUTINE_DUMP bool __stdcall DllMain(HANDLE hModule, DWORD ul_reason_for_call, LPVOID lpReserved);

#ifdef __cplusplus
}
#endif

#endif
