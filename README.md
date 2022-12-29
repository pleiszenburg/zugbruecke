![zugbruecke](docs/source/_static/logo.png "zugbruecke logo")

# zugbruecke

**Calling routines in Windows DLLs from Python scripts running under Linux, MacOS or BSD**

*/ˈt͡suːkˌbʁʏkə/ ([German, noun, feminine: drawbridge](https://dict.leo.org/englisch-deutsch/zugbrücke))*

[![build_master](https://github.com/pleiszenburg/zugbruecke/actions/workflows/test.yaml/badge.svg?branch=master "Build Status: master / release")](https://github.com/pleiszenburg/zugbruecke/actions/workflows/test.yaml)
[![docs_master](https://readthedocs.org/projects/zugbruecke/badge/?version=latest&style=flat-square "Documentation Status: master / release")](https://zugbruecke.readthedocs.io/en/latest/?badge=latest)
[![license](https://img.shields.io/pypi/l/zugbruecke.svg?style=flat-square "Project License: LGPLv2")](https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE)
[![status](https://img.shields.io/pypi/status/zugbruecke.svg?style=flat-square "Project Development Status")](https://github.com/pleiszenburg/zugbruecke/milestone/1)
[![pypi_version](https://img.shields.io/pypi/v/zugbruecke.svg?style=flat-square "Available on PyPi - the Python Package Index")](https://pypi.python.org/pypi/zugbruecke)
[![pypi_versions](https://img.shields.io/pypi/pyversions/zugbruecke.svg?style=flat-square "Available on PyPi - the Python Package Index")](https://pypi.python.org/pypi/zugbruecke)
[![chat](https://img.shields.io/matrix/zugbruecke:matrix.org.svg?style=flat-square "Matrix Chat Room")](https://matrix.to/#/#zugbruecke:matrix.org)
[![mailing_list](https://img.shields.io/badge/mailing%20list-groups.io-8cbcd1.svg?style=flat-square "Mailing List")](https://groups.io/g/zugbruecke-dev)

## Synopsis

**zugbruecke** is an EXPERIMENTAL **Python package** (currently in development **status 3/alpha**). It allows to **call routines in Windows DLLs from Python code running on Unices / Unix-like systems** such as Linux, MacOS or BSD. `zugbruecke` is designed as a **drop-in replacement for Python's standard library's ctypes module**. `zugbruecke` is **built on top of Wine**. A stand-alone Windows Python interpreter launched in the background is used to execute the called DLL routines. Communication between the Unix-side and the Windows/Wine-side is based on Python's build-in multiprocessing connection capability. `zugbruecke` has (limited) support for pointers, struct types and call-back functions. `zugbruecke` comes with extensive logging features allowing to debug problems associated with both itself and with Wine. `zugbruecke` is written using **Python 3 syntax** and primarily targets the **CPython** implementation of Python.

About Wine (from [winehq.org](https://www.winehq.org/)): *Wine (originally an acronym for "Wine Is Not an Emulator") is a compatibility layer capable of running Windows applications on several POSIX-compliant operating systems, such as Linux, MacOS and BSD. Instead of simulating internal Windows logic like a virtual machine or emulator, Wine translates Windows API calls into POSIX calls on-the-fly, eliminating the performance and memory penalties of other methods and allowing you to cleanly integrate Windows applications into your desktop.*

**This project is NEITHER associated NOR affiliated in any way or form with the Wine project.**

## Prerequisites

| type | prerequisite | version |
| --- | --- | --- |
| user | [CPython](https://www.python.org/) | 3.x (tested with 3.{7,8,9,10,11}) |
| user | [Wine](https://www.winehq.org/) | >= 6.x (tested with regular & [staging](https://wine-staging.com/)) - expected to be in the user's [`PATH`](https://en.wikipedia.org/wiki/PATH_(variable)) |
| developer | [mingw cross-compiler](https://mxe.cc) | For building DLLs against which examples and tests can be run. Latest stable release. |

## Installation

| branch | status | installation | documentation |
| --- | --- | --- | --- |
| master (release) | [![build_master](https://github.com/pleiszenburg/zugbruecke/actions/workflows/test.yaml/badge.svg?branch=master "Build Status: master / release")](https://github.com/pleiszenburg/zugbruecke/tree/master) | `pip install zugbruecke` | [![docs_master](https://readthedocs.org/projects/zugbruecke/badge/?version=latest&style=flat-square "Documentation Status: master / release")](https://zugbruecke.readthedocs.io/en/latest/) |
| develop | [![build_develop](https://github.com/pleiszenburg/zugbruecke/actions/workflows/test.yaml/badge.svg?branch=develop "Build Status: development branch")](https://github.com/pleiszenburg/zugbruecke/tree/develop) | `pip install git+https://github.com/pleiszenburg/zugbruecke.git@develop` | [![docs_develop](https://readthedocs.org/projects/zugbruecke/badge/?version=develop&style=flat-square "Documentation Status: development branch")](https://zugbruecke.readthedocs.io/en/develop/) |

After installing the package with `pip`, you may choose to manually initialize the *Wine Python environment* by running `wenv init`. If you choose not to do this, `zugbruecke` will take care of it during its first use.

## Example

Start an interactive Python session on your favorite Unix(-like) operating system and try the following:

```python
import zugbruecke.ctypes as ctypes
dll_pow = ctypes.cdll.msvcrt.pow
dll_pow.argtypes = (ctypes.c_double, ctypes.c_double)
dll_pow.restype = ctypes.c_double
print(f'You should expect "1024.0" to show up here: "{dll_pow(2.0, 10.0):.1f}".')
```

You have just witnessed `msvcrt.dll`, Microsoft's C standard library (or Wine's implementation of it), in action on Unix.

### Interested in more?

- Check the [Getting Started](https://zugbruecke.readthedocs.io/en/stable/examples.html) section in `zugbruecke`'s documentation,
- Read [ctypes' documentation](https://docs.python.org/3/library/ctypes.html),
- Beyond `ctypes` syntax, learn about [memory synchronization](https://zugbruecke.readthedocs.io/en/latest/memsync.html) with the `memsync` routine attribute (or)
- Have a look at `zugbruecke`'s [test suite](https://github.com/pleiszenburg/zugbruecke/tree/master/tests) showcasing its entire range of capabilities.

A lot of code, which was written with `ctypes`' `cdll`, `windll` or `oledll` in mind and which runs under Windows, should run just fine with `zugbruecke` on Unix (assuming it does not use Windows features not supported by Wine). For more complex calls, [memory synchronization](https://zugbruecke.readthedocs.io/en/latest/memsync.html) is potentially necessary.

## Speed

`zugbruecke` performs reasonably well given its complexity with **around 0.15 ms overhead per simple call** on average on modern hardware. For significantly more complex calls, the overhead can go into several milliseconds. `zugbruecke` is not (yet) optimized for speed. Check the latest [benchmarks](https://zugbruecke.readthedocs.io/en/stable/benchmarks.html) for more details.

## Security

`zugbruecke` is **notoriously insecure**. Never, ever, run it with root / super users privileges! Do not use it where security matters! For details, check the section on [security](https://zugbruecke.readthedocs.io/en/stable/security.html) in the documentation.

## Need help?

See section on [Getting Help](https://zugbruecke.readthedocs.io/en/latest/support.html) on `zugbruecke`'s documentation.

## Bugs & Issues

See section on [Bugs and Issues](https://zugbruecke.readthedocs.io/en/stable/bugs.html) on `zugbruecke`'s documentation.

## Miscellaneous

- Full project documentation
  - at [Read the Docs](https://zugbruecke.readthedocs.io/en/latest/)
  - at [`zugbruecke` repository](https://github.com/pleiszenburg/zugbruecke/blob/master/docs/source/index.rst)
- [Authors](https://github.com/pleiszenburg/zugbruecke/blob/master/AUTHORS.md)
- [Change log (current)](https://github.com/pleiszenburg/zugbruecke/blob/develop/CHANGES.md) (changes in development branch since last release)
- [Change log (past)](https://github.com/pleiszenburg/zugbruecke/blob/master/CHANGES.md) (release history)
- [Contributing](https://github.com/pleiszenburg/zugbruecke/blob/master/CONTRIBUTING.md) (**Contributions are highly welcomed!**)
- [FAQ](https://zugbruecke.readthedocs.io/en/stable/faq.html)
- [License](https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE) (**LGPL v2.1**)
- [Long-term ideas](https://github.com/pleiszenburg/zugbruecke/milestone/2)
- [Missing features](https://github.com/pleiszenburg/zugbruecke/issues?q=is%3Aissue+is%3Aopen+label%3A%22missing+ctypes+feature%22) (for full ctypes compatibility)
- [Upstream issues](https://github.com/pleiszenburg/zugbruecke/issues?q=is%3Aissue+is%3Aopen+label%3Aupstream) (relevant bugs in dependencies)

## For production environments

**DO NOT run this code (as-is) in production environments unless you feel that you really know what you are doing (or unless you are absolutely desperate)! Being experimental in nature and of alpha quality, it is prone to fail in a number of unpredictable ways, some of which might not be obvious or might not even show any (intermediately) recognizable symptoms at all! You might end up with plain wrong, nonsensical results without noticing it! Verify and cross-check your results!**

`zugbruecke` is using **semantic versioning**. Breaking changes are indicated by increasing the second version number, the minor version. Going for example from 0.0.x to 0.1.y or going from 0.1.x to 0.2.y therefore indicates a breaking change. For as long as `zugbruecke` has development status "alpha", please expect more breaking changes to come.

If you are relying on `zugbruecke` in one way or another, please consider monitoring the project: [its repository on Github](https://github.com/pleiszenburg/zugbruecke), [its mailing list](https://groups.io/g/zugbruecke-dev) and [its chatroom](https://matrix.to/#/#zugbruecke:matrix.org).
