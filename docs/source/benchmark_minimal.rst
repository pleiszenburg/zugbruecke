.. csv-table:: "minimal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 0.7; 182.0; 181.3
    "3.7.9"; "win32"; "windll"; 0.7; 151.6; 150.9
    "3.7.9"; "win64"; "cdll"; 0.6; 137.7; 137.1
    "3.7.9"; "win64"; "windll"; 0.6; 142.4; 141.8
    "3.8.10"; "win32"; "cdll"; 0.7; 178.3; 177.6
    "3.8.10"; "win32"; "windll"; 0.7; 150.9; 150.2
    "3.8.10"; "win64"; "cdll"; 0.5; 132.5; 132.0
    "3.8.10"; "win64"; "windll"; 0.5; 136.4; 135.9
    "3.9.13"; "win32"; "cdll"; 0.7; 145.1; 144.4
    "3.9.13"; "win32"; "windll"; 0.7; 150.8; 150.1
    "3.9.13"; "win64"; "cdll"; 0.5; 138.9; 138.4
    "3.9.13"; "win64"; "windll"; 0.5; 136.1; 135.6
    "3.10.9"; "win32"; "cdll"; 0.7; 181.4; 180.7
    "3.10.9"; "win32"; "windll"; 0.7; 151.2; 150.5
    "3.10.9"; "win64"; "cdll"; 0.5; 138.2; 137.7
    "3.10.9"; "win64"; "windll"; 0.5; 130.8; 130.3
    "3.11.1"; "win32"; "cdll"; 0.7; 146.7; 146.0
    "3.11.1"; "win32"; "windll"; 0.7; 146.8; 146.1
    "3.11.1"; "win64"; "cdll"; 0.5; 134.7; 134.2
    "3.11.1"; "win64"; "windll"; 0.5; 128.6; 128.1


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

