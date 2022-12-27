.. csv-table:: "maximal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "3.7.9"; "win32"; "cdll"; 171; 5,708; 5,537
    "3.7.9"; "win32"; "windll"; 171; 5,226; 5,055
    "3.7.9"; "win64"; "cdll"; 139; 5,257; 5,118
    "3.7.9"; "win64"; "windll"; 141; 5,140; 4,999
    "3.8.10"; "win32"; "cdll"; 152; 5,298; 5,146
    "3.8.10"; "win32"; "windll"; 152; 5,037; 4,885
    "3.8.10"; "win64"; "cdll"; 130; 4,815; 4,685
    "3.8.10"; "win64"; "windll"; 130; 4,840; 4,710
    "3.9.13"; "win32"; "cdll"; 140; 4,961; 4,821
    "3.9.13"; "win32"; "windll"; 140; 5,109; 4,969
    "3.9.13"; "win64"; "cdll"; 134; 5,113; 4,979
    "3.9.13"; "win64"; "windll"; 134; 5,059; 4,925
    "3.10.9"; "win32"; "cdll"; 156; 5,872; 5,716
    "3.10.9"; "win32"; "windll"; 156; 5,130; 4,974
    "3.10.9"; "win64"; "cdll"; 136; 5,708; 5,572
    "3.10.9"; "win64"; "windll"; 136; 4,878; 4,742
    "3.11.1"; "win32"; "cdll"; 150; 4,928; 4,778
    "3.11.1"; "win32"; "windll"; 150; 4,876; 4,726
    "3.11.1"; "win64"; "cdll"; 131; 4,504; 4,373
    "3.11.1"; "win64"; "windll"; 132; 4,562; 4,430


The "maximal" benchmark runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 9 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 3x3 pixel monochrom image while the filter's kernel is provided by the callback function.

