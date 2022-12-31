.. csv-table:: "maximal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 67.3; 2,573.5; 2,506.2
    "3.7.9"; "win32"; "windll"; 66.8; 2,578.1; 2,511.3
    "3.7.9"; "win64"; "cdll"; 49.9; 2,301.9; 2,252.0
    "3.7.9"; "win64"; "windll"; 51.4; 2,313.5; 2,262.1
    "3.8.10"; "win32"; "cdll"; 59.9; 2,406.5; 2,346.6
    "3.8.10"; "win32"; "windll"; 60.5; 2,402.5; 2,342.0
    "3.8.10"; "win64"; "cdll"; 45.2; 2,166.9; 2,121.7
    "3.8.10"; "win64"; "windll"; 44.7; 2,181.1; 2,136.4
    "3.9.13"; "win32"; "cdll"; 59.6; 2,434.6; 2,375.0
    "3.9.13"; "win32"; "windll"; 59.8; 2,415.7; 2,355.9
    "3.9.13"; "win64"; "cdll"; 45.9; 2,187.5; 2,141.6
    "3.9.13"; "win64"; "windll"; 45.6; 2,188.5; 2,142.9
    "3.10.9"; "win32"; "cdll"; 62.6; 2,361.9; 2,299.3
    "3.10.9"; "win32"; "windll"; 62.5; 2,439.2; 2,376.7
    "3.10.9"; "win64"; "cdll"; 47.0; 2,177.9; 2,130.9
    "3.10.9"; "win64"; "windll"; 46.5; 2,173.7; 2,127.2
    "3.11.1"; "win32"; "cdll"; 58.5; 2,490.1; 2,431.6
    "3.11.1"; "win32"; "windll"; 58.6; 2,347.9; 2,289.3
    "3.11.1"; "win64"; "cdll"; 42.7; 2,113.6; 2,070.9
    "3.11.1"; "win64"; "windll"; 42.7; 2,123.4; 2,080.7


The "maximal" benchmark runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 9 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 3x3 pixel monochrom image while the filter's kernel is provided by the callback function.

