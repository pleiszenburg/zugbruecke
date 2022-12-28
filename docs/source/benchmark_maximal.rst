.. csv-table:: "maximal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 68.6; 2,361.1; 2,292.5
    "3.7.9"; "win32"; "windll"; 68.5; 2,397.2; 2,328.7
    "3.7.9"; "win64"; "cdll"; 49.9; 2,172.2; 2,122.3
    "3.7.9"; "win64"; "windll"; 50.5; 2,221.8; 2,171.3
    "3.8.10"; "win32"; "cdll"; 60.6; 2,323.8; 2,263.2
    "3.8.10"; "win32"; "windll"; 61.1; 2,307.3; 2,246.2
    "3.8.10"; "win64"; "cdll"; 44.7; 2,080.9; 2,036.2
    "3.8.10"; "win64"; "windll"; 44.5; 1,996.2; 1,951.7
    "3.9.13"; "win32"; "cdll"; 59.9; 2,191.3; 2,131.4
    "3.9.13"; "win32"; "windll"; 59.0; 2,288.8; 2,229.8
    "3.9.13"; "win64"; "cdll"; 46.2; 1,934.7; 1,888.5
    "3.9.13"; "win64"; "windll"; 45.3; 1,984.7; 1,939.4
    "3.10.9"; "win32"; "cdll"; 62.2; 2,211.9; 2,149.7
    "3.10.9"; "win32"; "windll"; 62.5; 2,291.7; 2,229.2
    "3.10.9"; "win64"; "cdll"; 46.6; 2,006.7; 1,960.1
    "3.10.9"; "win64"; "windll"; 46.3; 2,017.7; 1,971.4
    "3.11.1"; "win32"; "cdll"; 58.1; 2,150.1; 2,092.0
    "3.11.1"; "win32"; "windll"; 58.5; 2,468.0; 2,409.5
    "3.11.1"; "win64"; "cdll"; 42.5; 1,944.1; 1,901.6
    "3.11.1"; "win64"; "windll"; 42.6; 1,902.0; 1,859.4


The "maximal" benchmark runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 9 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 3x3 pixel monochrom image while the filter's kernel is provided by the callback function.

