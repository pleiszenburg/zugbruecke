.. csv-table:: "minimal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 0.7; 152.1; 151.4
    "3.7.9"; "win32"; "windll"; 0.7; 152.4; 151.7
    "3.7.9"; "win64"; "cdll"; 0.6; 136.9; 136.3
    "3.7.9"; "win64"; "windll"; 0.6; 135.8; 135.2
    "3.8.10"; "win32"; "cdll"; 0.7; 148.7; 148.0
    "3.8.10"; "win32"; "windll"; 0.7; 146.2; 145.5
    "3.8.10"; "win64"; "cdll"; 0.5; 133.0; 132.5
    "3.8.10"; "win64"; "windll"; 0.5; 131.8; 131.3
    "3.9.13"; "win32"; "cdll"; 0.7; 145.8; 145.1
    "3.9.13"; "win32"; "windll"; 0.7; 143.5; 142.8
    "3.9.13"; "win64"; "cdll"; 0.5; 130.8; 130.3
    "3.9.13"; "win64"; "windll"; 0.5; 126.2; 125.7
    "3.10.9"; "win32"; "cdll"; 0.7; 146.8; 146.1
    "3.10.9"; "win32"; "windll"; 0.7; 143.0; 142.3
    "3.10.9"; "win64"; "cdll"; 0.5; 134.5; 134.0
    "3.10.9"; "win64"; "windll"; 0.5; 130.2; 129.7
    "3.11.1"; "win32"; "cdll"; 0.7; 147.0; 146.3
    "3.11.1"; "win32"; "windll"; 0.6; 138.4; 137.8
    "3.11.1"; "win64"; "cdll"; 0.5; 131.7; 131.2
    "3.11.1"; "win64"; "windll"; 0.5; 126.9; 126.4


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

