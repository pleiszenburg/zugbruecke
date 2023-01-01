.. csv-table:: "minimal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 0.7; 151.8; 151.1
    "3.7.9"; "win32"; "windll"; 0.7; 143.5; 142.8
    "3.7.9"; "win64"; "cdll"; 0.6; 132.1; 131.5
    "3.7.9"; "win64"; "windll"; 0.6; 133.7; 133.1
    "3.8.10"; "win32"; "cdll"; 0.7; 143.1; 142.4
    "3.8.10"; "win32"; "windll"; 0.7; 139.2; 138.5
    "3.8.10"; "win64"; "cdll"; 0.5; 128.4; 127.9
    "3.8.10"; "win64"; "windll"; 0.5; 132.5; 132.0
    "3.9.13"; "win32"; "cdll"; 0.7; 146.8; 146.1
    "3.9.13"; "win32"; "windll"; 0.7; 147.3; 146.6
    "3.9.13"; "win64"; "cdll"; 0.5; 130.4; 129.9
    "3.9.13"; "win64"; "windll"; 0.5; 135.0; 134.5
    "3.10.9"; "win32"; "cdll"; 0.7; 146.2; 145.5
    "3.10.9"; "win32"; "windll"; 0.7; 146.1; 145.4
    "3.10.9"; "win64"; "cdll"; 0.5; 139.1; 138.6
    "3.10.9"; "win64"; "windll"; 0.5; 131.5; 131.0
    "3.11.1"; "win32"; "cdll"; 0.7; 142.5; 141.8
    "3.11.1"; "win32"; "windll"; 0.7; 142.5; 141.8
    "3.11.1"; "win64"; "cdll"; 0.5; 131.8; 131.3
    "3.11.1"; "win64"; "windll"; 0.5; 133.8; 133.3


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

