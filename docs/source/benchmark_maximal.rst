.. csv-table:: "maximal" benchmark, CPython 3.10.6 on linux, versions of CPython on Wine
    :header: "arch", "version", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"
    :delim: 0x0003B

    "win32"; "3.7.9"; "cdll"; 1,637; 57,695; 56,058
    "win32"; "3.7.9"; "windll"; 1,636; 59,121; 57,485
    "win32"; "3.8.10"; "cdll"; 1,493; 54,029; 52,536
    "win32"; "3.8.10"; "windll"; 1,486; 55,027; 53,541
    "win32"; "3.9.13"; "cdll"; 1,319; 52,984; 51,665
    "win32"; "3.9.13"; "windll"; 1,322; 55,137; 53,815
    "win32"; "3.10.9"; "cdll"; 1,497; 55,747; 54,250
    "win32"; "3.10.9"; "windll"; 1,494; 55,520; 54,026
    "win32"; "3.11.1"; "cdll"; 1,453; 52,746; 51,293
    "win32"; "3.11.1"; "windll"; 1,458; 52,314; 50,856
    "win64"; "3.7.9"; "cdll"; 1,321; 55,946; 54,625
    "win64"; "3.7.9"; "windll"; 1,329; 54,258; 52,929
    "win64"; "3.8.10"; "cdll"; 1,220; 52,559; 51,339
    "win64"; "3.8.10"; "windll"; 1,222; 52,217; 50,995
    "win64"; "3.9.13"; "cdll"; 1,278; 49,920; 48,642
    "win64"; "3.9.13"; "windll"; 1,288; 50,703; 49,415
    "win64"; "3.10.9"; "cdll"; 1,305; 53,682; 52,377
    "win64"; "3.10.9"; "windll"; 1,299; 50,330; 49,031
    "win64"; "3.11.1"; "cdll"; 1,240; 50,350; 49,110
    "win64"; "3.11.1"; "windll"; 1,242; 51,180; 49,938


The "maximal" benchmark runs through everything that *zugbuecke* has to offer.
The DLL function takes three arguments: Two pointers to structs and a function pointer.
The structs themselves contain pointers to memory of arbitrary length which is handled by ``memsync``.
The function pointer allows to pass a reference to a callback function, written in pure Python.
It takes a single pointer to a struct, again containing a pointer to memory of arbitrary length,
yet again handled by ``memsync``, and returns a single integer.
The callback is invoked 100 times per DLL function call.
The test is based on a simple monochrom image filter where the DLL function iterates over every pixel
in a 10x10 pixel monochrom image while the filter's kernel is provided by the callback function.

