.. csv-table:: "memsync" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 11.6; 201.0; 189.4
    "3.7.9"; "win32"; "windll"; 11.6; 205.7; 194.1
    "3.7.9"; "win64"; "cdll"; 8.6; 185.4; 176.8
    "3.7.9"; "win64"; "windll"; 8.4; 186.7; 178.3
    "3.8.10"; "win32"; "cdll"; 10.1; 192.4; 182.3
    "3.8.10"; "win32"; "windll"; 10.0; 199.7; 189.7
    "3.8.10"; "win64"; "cdll"; 7.2; 180.1; 172.9
    "3.8.10"; "win64"; "windll"; 7.1; 179.7; 172.6
    "3.9.13"; "win32"; "cdll"; 9.4; 195.1; 185.7
    "3.9.13"; "win32"; "windll"; 9.4; 203.7; 194.3
    "3.9.13"; "win64"; "cdll"; 7.2; 174.4; 167.2
    "3.9.13"; "win64"; "windll"; 7.1; 180.3; 173.2
    "3.10.9"; "win32"; "cdll"; 9.8; 194.8; 185.0
    "3.10.9"; "win32"; "windll"; 9.7; 200.1; 190.4
    "3.10.9"; "win64"; "cdll"; 7.3; 183.3; 176.0
    "3.10.9"; "win64"; "windll"; 7.3; 180.3; 173.0
    "3.11.1"; "win32"; "cdll"; 9.4; 190.8; 181.4
    "3.11.1"; "win32"; "windll"; 9.3; 193.1; 183.8
    "3.11.1"; "win64"; "cdll"; 7.2; 179.7; 172.5
    "3.11.1"; "win64"; "windll"; 7.2; 176.7; 169.5


The "memsync" benchmark is a basic test of bidirectional memory synchronization
via a ``memsync`` directive for a pointer argument,
an array of single-precision floating point numbers.
The benchmark uses 10 numbers per array.
It is passed to the DLL function,
next to the array's length as an ``c_int``.
The DLL function performs a classic bubblesort algorithm in-place
on the passed / synchronized memory.

