.. csv-table:: "minimal" benchmarks, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "arch", "version", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "win32"; "3.7.9"; "cdll"; 2; 374; 372
    "win32"; "3.7.9"; "windll"; 2; 373; 371
    "win32"; "3.8.10"; "cdll"; 2; 368; 366
    "win32"; "3.8.10"; "windll"; 2; 369; 367
    "win32"; "3.9.13"; "cdll"; 2; 364; 362
    "win32"; "3.9.13"; "windll"; 2; 364; 362
    "win32"; "3.10.9"; "cdll"; 2; 365; 363
    "win32"; "3.10.9"; "windll"; 2; 366; 364
    "win32"; "3.11.1"; "cdll"; 2; 357; 355
    "win32"; "3.11.1"; "windll"; 2; 358; 356
    "win64"; "3.7.9"; "cdll"; 1; 356; 355
    "win64"; "3.7.9"; "windll"; 1; 357; 356
    "win64"; "3.8.10"; "cdll"; 1; 349; 348
    "win64"; "3.8.10"; "windll"; 1; 348; 347
    "win64"; "3.9.13"; "cdll"; 1; 349; 348
    "win64"; "3.9.13"; "windll"; 1; 349; 348
    "win64"; "3.10.9"; "cdll"; 1; 349; 348
    "win64"; "3.10.9"; "windll"; 1; 350; 349
    "win64"; "3.11.1"; "cdll"; 1; 344; 343
    "win64"; "3.11.1"; "windll"; 1; 345; 344


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

