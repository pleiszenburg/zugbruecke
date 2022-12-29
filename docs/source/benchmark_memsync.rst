.. csv-table:: "memsync" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 11.4; 210.3; 198.9
    "3.7.9"; "win32"; "windll"; 11.5; 210.2; 198.7
    "3.7.9"; "win64"; "cdll"; 8.9; 194.7; 185.8
    "3.7.9"; "win64"; "windll"; 8.7; 194.0; 185.3
    "3.8.10"; "win32"; "cdll"; 10.2; 203.3; 193.1
    "3.8.10"; "win32"; "windll"; 10.1; 203.9; 193.8
    "3.8.10"; "win64"; "cdll"; 7.5; 186.1; 178.6
    "3.8.10"; "win64"; "windll"; 7.4; 186.2; 178.8
    "3.9.13"; "win32"; "cdll"; 9.4; 201.5; 192.1
    "3.9.13"; "win32"; "windll"; 9.4; 204.0; 194.6
    "3.9.13"; "win64"; "cdll"; 7.2; 184.6; 177.4
    "3.9.13"; "win64"; "windll"; 7.0; 183.0; 176.0
    "3.10.9"; "win32"; "cdll"; 9.9; 203.2; 193.3
    "3.10.9"; "win32"; "windll"; 9.9; 203.8; 193.9
    "3.10.9"; "win64"; "cdll"; 7.5; 183.0; 175.5
    "3.10.9"; "win64"; "windll"; 7.4; 184.3; 176.9
    "3.11.1"; "win32"; "cdll"; 9.3; 200.5; 191.2
    "3.11.1"; "win32"; "windll"; 9.3; 197.5; 188.2
    "3.11.1"; "win64"; "cdll"; 7.3; 185.4; 178.1
    "3.11.1"; "win64"; "windll"; 7.2; 184.6; 177.4


The "memsync" benchmark is a basic test of bidirectional memory synchronization
via a ``memsync`` directive for a pointer argument,
an array of single-precision floating point numbers.
The benchmark uses 10 numbers per array.
It is passed to the DLL function,
next to the array's length as an ``c_int``.
The DLL function performs a classic bubblesort algorithm in-place
on the passed / synchronized memory.

