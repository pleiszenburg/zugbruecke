.. csv-table:: "maximal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 67.6; 2,498.4; 2,430.8
    "3.7.9"; "win32"; "windll"; 67.4; 2,564.9; 2,497.5
    "3.7.9"; "win64"; "cdll"; 50.0; 2,191.9; 2,141.9
    "3.7.9"; "win64"; "windll"; 50.1; 2,215.1; 2,165.0
    "3.8.10"; "win32"; "cdll"; 60.7; 2,317.8; 2,257.1
    "3.8.10"; "win32"; "windll"; 61.4; 2,441.7; 2,380.3
    "3.8.10"; "win64"; "cdll"; 44.5; 2,101.1; 2,056.6
    "3.8.10"; "win64"; "windll"; 44.3; 2,430.5; 2,386.2
    "3.9.13"; "win32"; "cdll"; 59.6; 2,311.1; 2,251.5
    "3.9.13"; "win32"; "windll"; 59.4; 2,382.9; 2,323.5
    "3.9.13"; "win64"; "cdll"; 45.0; 2,052.9; 2,007.9
    "3.9.13"; "win64"; "windll"; 44.8; 2,377.7; 2,332.9
    "3.10.9"; "win32"; "cdll"; 61.9; 2,293.4; 2,231.5
    "3.10.9"; "win32"; "windll"; 62.2; 2,429.5; 2,367.3
    "3.10.9"; "win64"; "cdll"; 46.3; 2,042.8; 1,996.5
    "3.10.9"; "win64"; "windll"; 46.4; 2,350.4; 2,304.0
    "3.11.1"; "win32"; "cdll"; 58.7; 2,268.0; 2,209.3
    "3.11.1"; "win32"; "windll"; 58.5; 2,343.3; 2,284.8
    "3.11.1"; "win64"; "cdll"; 42.3; 1,991.9; 1,949.6
    "3.11.1"; "win64"; "windll"; 41.9; 2,075.1; 2,033.2


The "maximal" benchmark runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 9 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 3x3 pixel monochrom image while the filter's kernel is provided by the callback function.

