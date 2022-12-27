.. csv-table:: "maximal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "arch", "version", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "win32"; "3.7.9"; "cdll"; 1,634; 54,424; 52,790
    "win32"; "3.7.9"; "windll"; 1,631; 52,090; 50,459
    "win32"; "3.8.10"; "cdll"; 1,484; 49,120; 47,636
    "win32"; "3.8.10"; "windll"; 1,481; 49,039; 47,558
    "win32"; "3.9.13"; "cdll"; 1,329; 49,139; 47,810
    "win32"; "3.9.13"; "windll"; 1,330; 49,727; 48,397
    "win32"; "3.10.9"; "cdll"; 1,500; 51,282; 49,782
    "win32"; "3.10.9"; "windll"; 1,499; 50,262; 48,763
    "win32"; "3.11.1"; "cdll"; 1,459; 47,481; 46,022
    "win32"; "3.11.1"; "windll"; 1,461; 47,619; 46,158
    "win64"; "3.7.9"; "cdll"; 1,338; 49,060; 47,722
    "win64"; "3.7.9"; "windll"; 1,347; 48,996; 47,649
    "win64"; "3.8.10"; "cdll"; 1,251; 48,973; 47,722
    "win64"; "3.8.10"; "windll"; 1,252; 47,132; 45,880
    "win64"; "3.9.13"; "cdll"; 1,273; 46,872; 45,599
    "win64"; "3.9.13"; "windll"; 1,285; 46,518; 45,233
    "win64"; "3.10.9"; "cdll"; 1,301; 46,324; 45,023
    "win64"; "3.10.9"; "windll"; 1,296; 47,465; 46,169
    "win64"; "3.11.1"; "cdll"; 1,249; 45,970; 44,721
    "win64"; "3.11.1"; "windll"; 1,256; 44,271; 43,015


The "maximal" benchmark runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 100 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 10x10 pixel monochrom image while the filter's kernel is provided by the callback function.

