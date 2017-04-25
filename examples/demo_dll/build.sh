#!/bin/bash

/usr/bin/i686-w64-mingw32-gcc -Wall -Wl,-add-stdcall-alias -shared demo_dll.c -o demo_dll.dll
