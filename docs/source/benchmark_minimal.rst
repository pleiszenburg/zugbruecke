.. csv-table:: "minimal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 2; 386; 384
    "3.7.9"; "win32"; "windll"; 2; 345; 343
    "3.7.9"; "win64"; "cdll"; 1; 330; 329
    "3.7.9"; "win64"; "windll"; 1; 337; 336
    "3.8.10"; "win32"; "cdll"; 2; 384; 382
    "3.8.10"; "win32"; "windll"; 2; 338; 336
    "3.8.10"; "win64"; "cdll"; 1; 321; 320
    "3.8.10"; "win64"; "windll"; 1; 322; 321
    "3.9.13"; "win32"; "cdll"; 2; 336; 334
    "3.9.13"; "win32"; "windll"; 2; 336; 334
    "3.9.13"; "win64"; "cdll"; 1; 324; 323
    "3.9.13"; "win64"; "windll"; 1; 321; 320
    "3.10.9"; "win32"; "cdll"; 2; 338; 336
    "3.10.9"; "win32"; "windll"; 2; 339; 337
    "3.10.9"; "win64"; "cdll"; 1; 324; 323
    "3.10.9"; "win64"; "windll"; 1; 323; 322
    "3.11.1"; "win32"; "cdll"; 2; 329; 327
    "3.11.1"; "win32"; "windll"; 2; 330; 328
    "3.11.1"; "win64"; "cdll"; 1; 316; 315
    "3.11.1"; "win64"; "windll"; 1; 322; 321


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

