.. csv-table:: "maximal" benchmarks, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "arch", "version", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "win32"; "3.7.9"; "cdll"; 1,559; 64,090; 62,531
    "win32"; "3.7.9"; "windll"; 1,564; 58,570; 57,006
    "win32"; "3.8.10"; "cdll"; 1,484; 56,556; 55,072
    "win32"; "3.8.10"; "windll"; 1,479; 57,946; 56,467
    "win32"; "3.9.13"; "cdll"; 1,329; 56,506; 55,177
    "win32"; "3.9.13"; "windll"; 1,332; 54,687; 53,355
    "win32"; "3.10.9"; "cdll"; 1,513; 55,953; 54,440
    "win32"; "3.10.9"; "windll"; 1,509; 56,526; 55,017
    "win32"; "3.11.1"; "cdll"; 1,453; 52,882; 51,429
    "win32"; "3.11.1"; "windll"; 1,453; 53,613; 52,160
    "win64"; "3.7.9"; "cdll"; 1,343; 57,141; 55,798
    "win64"; "3.7.9"; "windll"; 1,341; 55,698; 54,357
    "win64"; "3.8.10"; "cdll"; 1,228; 52,543; 51,315
    "win64"; "3.8.10"; "windll"; 1,237; 50,628; 49,391
    "win64"; "3.9.13"; "cdll"; 1,276; 51,838; 50,562
    "win64"; "3.9.13"; "windll"; 1,284; 50,231; 48,947
    "win64"; "3.10.9"; "cdll"; 1,282; 55,638; 54,356
    "win64"; "3.10.9"; "windll"; 1,282; 51,042; 49,760
    "win64"; "3.11.1"; "cdll"; 1,244; 51,161; 49,917
    "win64"; "3.11.1"; "windll"; 1,252; 51,516; 50,264


The "maximal" benchmark is runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 100 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 10x10 pixel monochrom image while the filter's kernel is provided by the callback function.

