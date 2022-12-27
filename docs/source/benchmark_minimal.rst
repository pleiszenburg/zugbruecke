.. csv-table:: "minimal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "arch", "version", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "win32"; "3.7.9"; "cdll"; 2; 345; 343
    "win32"; "3.7.9"; "windll"; 2; 345; 343
    "win32"; "3.8.10"; "cdll"; 2; 383; 381
    "win32"; "3.8.10"; "windll"; 2; 336; 334
    "win32"; "3.9.13"; "cdll"; 2; 336; 334
    "win32"; "3.9.13"; "windll"; 2; 332; 330
    "win32"; "3.10.9"; "cdll"; 2; 337; 335
    "win32"; "3.10.9"; "windll"; 2; 336; 334
    "win32"; "3.11.1"; "cdll"; 2; 323; 321
    "win32"; "3.11.1"; "windll"; 2; 329; 327
    "win64"; "3.7.9"; "cdll"; 1; 313; 312
    "win64"; "3.7.9"; "windll"; 1; 328; 327
    "win64"; "3.8.10"; "cdll"; 1; 321; 320
    "win64"; "3.8.10"; "windll"; 1; 301; 300
    "win64"; "3.9.13"; "cdll"; 1; 323; 322
    "win64"; "3.9.13"; "windll"; 1; 322; 321
    "win64"; "3.10.9"; "cdll"; 1; 313; 312
    "win64"; "3.10.9"; "windll"; 1; 322; 321
    "win64"; "3.11.1"; "cdll"; 1; 318; 317
    "win64"; "3.11.1"; "windll"; 1; 318; 317


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

