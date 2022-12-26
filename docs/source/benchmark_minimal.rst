.. csv-table:: "minimal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "arch", "version", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "win32"; "3.7.9"; "cdll"; 2; 372; 370
    "win32"; "3.7.9"; "windll"; 2; 372; 370
    "win32"; "3.8.10"; "cdll"; 2; 368; 366
    "win32"; "3.8.10"; "windll"; 2; 365; 363
    "win32"; "3.9.13"; "cdll"; 2; 363; 361
    "win32"; "3.9.13"; "windll"; 2; 365; 363
    "win32"; "3.10.9"; "cdll"; 2; 365; 363
    "win32"; "3.10.9"; "windll"; 2; 365; 363
    "win32"; "3.11.1"; "cdll"; 2; 352; 350
    "win32"; "3.11.1"; "windll"; 2; 356; 354
    "win64"; "3.7.9"; "cdll"; 1; 357; 356
    "win64"; "3.7.9"; "windll"; 1; 356; 355
    "win64"; "3.8.10"; "cdll"; 1; 350; 349
    "win64"; "3.8.10"; "windll"; 1; 347; 346
    "win64"; "3.9.13"; "cdll"; 1; 346; 345
    "win64"; "3.9.13"; "windll"; 1; 347; 346
    "win64"; "3.10.9"; "cdll"; 1; 349; 348
    "win64"; "3.10.9"; "windll"; 1; 348; 347
    "win64"; "3.11.1"; "cdll"; 1; 346; 345
    "win64"; "3.11.1"; "windll"; 1; 344; 343


The "minimal" benchmark is a simple function call with
two ``c_int`` parameters and a single ``c_int`` return value.
The DLL function simply adds the two numbers and returns the result.

