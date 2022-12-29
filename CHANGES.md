# Changes

## 0.2.0 (2022-12-29)

**CAUTION**: A number changes at least partially **BREAK BACKWARDS COMPATIBILITY** for certain use and edge cases.

The datatype parser and definition code was rewritten completely. It should work as before in almost all instances although unexpected breakages may occur.

If entire struct objects are synced via `memsync` directives, the struct types now have to be specified directly instead of their names as strings as before, breaking backwards compatibility for those use cases.

*zugbruecke* now follows the Python's `logging` module's log levels. Maximum logging output can now be achieved via `logging.DEBUG` or `10` as opposed to `100` in earlier versions. Log level `0` remains as "no logs" as per `logging.NOTSET`. This change may break debugging and development workflows.

This **RELEASE FIXES A CRITICAL BUG** where *zugbruecke* was falsely translating 64 bit integer types from the Unix side to 32 bit integer types on the Wine side.

- FEATURE: Improved performance. With logging disabled, function calls carry 10% less overhead on average.
- FEATURE: In `memsync` directives, `ctypes` types do not need to be specified by their name as strings anymore - plain `ctypes` fundamental types and structure types can be used instead. Strings remain valid specifications for compatibility though.
- FEATURE: `memsync` directives allow for more descriptive parameter names while the old single-character names remain valid for compatibility.
- FEATURE: Added support for CPython 3.11, see #86 and #87.
- FEATURE: Logging now relies on Python's `logging` module's log levels, i.e. `NOTSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR` and `CRITICAL`. This change serves to work towards #84.
- FEATURE: Log output has been divided into log levels, see #9.
- FIX: Argtypes and restype would translate `c_int64`, `c_uint64`, `c_long` and `c_ulong` from the Unix side to their 32-bit equivalents, `c_int32` and `c_uint32`, on the Wine side. This was due to `c_long` and `c_ulong` being 8 bytes long on Unix-like systems while they are 4 bytes long on Window.
- FIX: Fixed-length `c_char` and `c_wchar` buffers passed by value within structures were not handled correctly, see #93.
- FIX: The new `argtypes` and `restype` parser does not suffer from #61 anymore where earlier different structure types from different name spaces but with identical names would cause problems.
- FIX: CI revealed that an issue similar to #50 returned as packages on Wine side can sometimes not be imported if they are symlinked. The new `copy_modules` configuration parameter can be used to indicate that a copy instead of symlinks is required. This problem is caused by [Wine bug #54228](https://bugs.winehq.org/show_bug.cgi?id=54228) in Wine Staging >= 7.18.
- FIX: If `zugbruecke` (and `wenv`) were installed into user site-packages, the installation would break, see #88.
- FIX: If writing of logs to disk (`log_write`) was set to `True` during run-time, `zugbruecke` would crash, see #77.
- FIX: Syncing entire structs via `memsync` was broken, see #92.
- FIX: `restype` was explicitly assumed to be `c_int`. Now, if a user does not specify it, assumptions about it are left to `ctypes` on the Wine side, potentially getting closer to `ctypes` original behaviour.
- FIX: `restype` would not throw an exception when by accident set to a list or tuple like original `ctypes` does.
- DEPRECATED: Single-character parameter names in memsync directives.
- DEPRECATED: `ctypes` fundamental types specified by name as strings in `memsync` directives.
- DOCS: More detailed explanation of `memsync`, where it is needed and where it is not, among other improvements.
- DOCS: Added explanation of handling of long integer types.
- DOCS: Added explanation of handling of floating point types and the lack of "long double" as well as "half precision" support.
- DOCS: Updated benchmarks.
- DOCS: Removed old `examples` folder from project as its code was more than outdated and can now be found in the documentation, the test suite and/or the newly added benchmarks.
- DEV: Added tests on custom types and `array.array` objects (standard library) as well as `numpy.ndarray` objects.
- DEV: Added tests for 64 bit integer limits / overflows for win64.
- DEV: Added tests on `restype` configuration errors.
- DEV: Cleaned and clarified all tests. Renamed all tests to more meaningful names referring to the features that they are testing.
- DEV: Test support library cleaned up, documented and typed.
- DEV: New benchmark infrastructure similar to the test suite, allowing to easily add benchmarks. Their results now get automatically included into the project documentation.

## 0.1.0 (2022-09-11)

**CAUTION**: The module layout changed, effectively **BREAKING BACKWARDS COMPATIBILITY** for all use-cases!

|                        | **OLD**                                           | **NEW**                                           |
| ---------------------- | ------------------------------------------------- | ------------------------------------------------- |
| default session        | `import zugbruecke as ctypes`                     | `import zugbruecke.ctypes as ctypes`              |
| default session member | `from zugbruecke import c_double`                 | `from zugbruecke.ctypes import c_double`          |
| ctypes session class   | `zugbruecke.session`                              | `zugbruecke.CtypesSession`                        |
| Wine Python            | `wine-python`                                     | `wenv python`                                     |
| Wine Pip               | `wine-pip`                                        | `wenv pip`                                        |
| Wine Pytest            | `wine-pytest`                                     | `wenv pytest`                                     |
| Wine Python shebang    | `#!/usr/bin/env wine-python`                      | `#!/usr/bin/env _wenv_python`                     |
| configuration          | `{"version": "3.5.3"}`                            | `{"pythonversion": "3.7.4"}`                      |

Significant changes were mandatory for allowing to **cleanup a lot of old code** and to **remove long-standing bugs**. The main issue was that importing `zugbruecke` would implicitly start a new session. This could not be prohibited. With the new package layout, it becomes possible to import sub-modules of `zugbruecke` without implicitly starting a session. One of the more significant added benefits therefore is that this also allows much more fine-grained tests.

`zugbruecke` will use **semantic versioning** from now on. Breaking changes will be indicated by increasing the second version number, the minor version. Going for example from 0.0.x to 0.1.y or going from 0.1.x to 0.2.y therefore indicates a breaking change. For as long as `zugbruecke` has development status "alpha", please expect more breaking changes to come.

- CLI: The shell scripts `wine-python`, `wine-pip` and `wine-pytest` have been consolidated into a **new Python package called** [wenv](https://wenv.readthedocs.io/en/latest/). One can now call `wenv python`, `wenv pip` and `wenv pytest`. This change was necessary for allowing a more generic interface to entry points of arbitrary third party packages. Run `wenv help` for more information. Changes related to `wenv` are now being tracked in **[wenv's change log](https://wenv.readthedocs.io/en/latest/changes.html)**. `wenv` has considerably more features and configuration options compared to the previously provided shell scripts.
- API: `zugbruecke.current_session` is no longer available. `zugbruecke.ctypes` on its own is now the default session. Besides, the class `zugbruecke.session` was renamed into `zugbruecke.CtypesSession` and has now a fully compatible `ctypes` drop-in replacement API as well. Both, `zugbruecke.ctypes` and custom sessions constructed from `zugbruecke.CtypesSession` now have methods and properties prefixed with `zb_` for manipulating their configuration, termination and Wine-related tasks.
- API: Configuration provided via environment variables is consistently preferred over everything else.
- API: The `set_parameter` method, now renamed into `zb_set_parameter`, only accepts a single key-value pair instead of a dictionary.
- API: The `version` configuration parameter for controlling the version of *Wine Python* has been renamed to `pythonversion`.
- FEATURE: All configuration parameters can be overridden with individual environment variables.
- FEATURE: Introduced new exception types specific to `zugbruecke`. Meaningful exception are now raised throughout the package.
- FEATURE: Timeouts for start and stop of the server component can be configured.
- FEATURE: Added support for CPython 3.10, see #75.
- FEATURE: Added support for CPython 3.9, see #74.
- FEATURE: Added support for CPython 3.8, see #56.
- FEATURE: Dropped support for CPython <= 3.6.
- FEATURE: Added support for Wine >= 6.0.
- FEATURE: Dropped support for Wine <= 5, most prominently Wine 4.
- FEATURE: `zugbruecke.CtypesSession` objects can be managed by context manager statements (`with`).
- FIX: `zugbruecke` did not capture and forward data coming from Windows DLLs and binaries through `stdout` and `stderr`(running with Wine) most of the time.
- FIX: A proper `TimeoutError` is raised (instead of a `SyntaxError`) if `zugbruecke`'s server component does not start.
- FIX: `zugbruecke` did not actually check properly if its server component had terminated when a session was terminated. The reliability of relevant termination code has been significantly improved.
- FIX: Methods from `zugbruecke.ctypes.util` (previously `zugbruecke.util`) are faster and a lot less error-prone, see #52.
- FIX: `zugbruecke.ctypes.CDLL` does no longer fall back to Unix libraries if no corresponding DLL file could be found. For attaching to Unix libraries please use the original `ctypes` module instead, see #53.
- FIX: Different structure types from different name spaces BUT identical names caused crashes, see #61.
- FIX: `zugbruecke` raised `TypeError` if too many arguments were given to a configured `cdll` function (`ctypes` does not), see #62.
- FIX: If a struct type was used in a function call with `memsync` first (before use in a function call without `memsync`), configuring (and calling) the function failed, see #63.
- FIX: Path conversion would fail for Wine 5.13 and later.
- FIX: Memory leak - sessions would collect all log data for as long as they were running, see #76.
- DOCS: Hugely improved.
- DOCS: Project mailing list and chat room.
- DEV: New `makefile` structure.
- DEV: All code is tested for both, 32bit (`win32`) and 64bit (`win64`) DLLs, see #58. Previously, only 32bit (`win32`) DLLs received regular testing.
- DEV: All code is tested for both, the `cdll`/`cdecl` and `windll`/`stdcall` calling conventions (previously only `windll`/`stdcall` received regular testing), see #60.
- DEV: `zugbruecke` is tested across all supported versions of CPython, both on Unix and on Wine side.
- DEV: The configuration module was refactored and made clearer and faster, allowing to implement new options.
- DEV: New debug mode, can be activated by setting the environment variable `ZUGBRUECKE_DEBUG` to `1`.
- DEV: Development dependency switch from unmaintained `python-language-server` to `python-lsp-server`.
- DEV: Both code and branch coverage of `zugbruecke` can now be analyzed with `coverage`.
- DEV: Moved from `setuptools` for packaging to `pyproject.toml` via `flit`.
- DEV: Cleanup of `docs` folder structure.
- DEV: Include logo in repo.

## 0.0.15 (2020-07-10)

- FIX: CI tests failed due to dependency issue in Python 3.4, see issue #72.

## 0.0.14 (2019-05-21)

- FIX: CI tests failed due to dependency link feature being dropped from `pip`, see issue #45.

## 0.0.13 (2019-02-03)

- FIX: Documentation could (sometimes) not be built on `readthedocs.org`.

## 0.0.12 (2019-02-02)

- FEATURE: Added support for CPython 3.7.
- FEATURE: Added support for Wine 4.
- FIX: Build folder was not automatically cleaned up before wheels were build, therefore they sometimes contained obsolete files & code.
- FIX: Travis configuration was missing new Wine repository key, which was breaking builds.
- DOCS: Lots of fixes in documentation.
- DEV: New test script for easier development of new tests and features.

## 0.0.11 (2018-04-10)

**CAUTION**: This release features a significant re-implementation (with additional, new functionality) of the memory synchronization protocol, ``memsync``.
As a part of it, overcoming old limitations, its syntax changed - effectively **BREAKING BACKWARDS COMPATIBILITY** in almost all cases.
Please check the updated documentation, examples and tests for details.

- API: `memsync` syntax for custom length functions has been changed. `_f` becomes obsolete. `f` expects a string, which can be parsed into a function.
- API: `memsync` syntax for NULL-terminated strings (both `c_char` and `c_wchar`, i.e. Unicode, buffers) has been simplified: `n` must be set to `True` indicating a NULL-terminated string. `l` becomes optional in this context.
- API: `memsync` syntax for Unicode strings (buffers) has been simplified: `w` must be set to `True` instead of the length of `ctypes.c_wchar`.
- FEATURE: `memsync` can handle pointers to memory, which was allocated by a DLL, see issue #37.
- FEATURE: `memsync` can target return values or elements within, see issue #40.
- FEATURE: `memsync` can be applied to callback functions, see issue #41 - support at this stage is largely untested.
- FEATURE: `memsync` became more memory efficient and slightly faster.

## 0.0.10 (2018-03-23)

- FEATURE: Support for functions calculating the length of memory sections in `memsync` protocol, see issue #33.
- FEATURE: Support for string buffers (and null-terminated strings), see issue #7.
- FIX: `memsync` definition sometimes lost information during first call of function, second call subsequently failed, see issue #36.

## 0.0.9 (2018-03-21)

**CAUTION**: This release introduces a change in configuration parameter naming, **BREAKING BACKWARDS COMPATIBILITY** in rare cases.

- API: Renamed `logwrite` parameter & command line option into `log_write`.
- FIX: Arch `win64` was broken because of wrong download URL for embedded CPython for win64/amd64, see issue #27.
- FIX: Function pointers in struct types were not handled, see issue #28.
- FIX: `memsync` directives pointing to elements within structs were not handled properly, see issue #29.
- FIX: Missing DLLs of type `windll` and `oledll` now raise `OSError` as expected, see issue #30.
- FIX: Missing routines in DLLs now raise `AttributeError` as expected, see issue #31.
- FIX: Wrong or unconfigured `argtypes` as well as wrong number of arguments do raise appropriate errors (`ValueError`, `ArgumentError` or `TypeError`), see issue #32.
- DEV: Isolated argument packing and unpacking code, preparing to solve issue #25.
- DEV: Reduced number of RPC servers to one per side (Unix and Wine).

## 0.0.8 (2018-03-18)

- FEATURE: Support for structures and pointers as return values, see issue #14.
- FEATURE: (Limited) support for call back functions (function pointers) as DLL argument types, see issues #3 and #4.
- FIX: `argtypes` definitions (with one single argument) were not raising a `TypeError` like `ctypes` does if not passed as a tuple or list, see issue #21.

## 0.0.7 (2018-03-05)

- FIX: Wine Python environment sometimes did, unintentionally, fall back to Python 2 and crash, see issue #20.
- Confirmed: Support for Mac OS X, see issue #16.

## 0.0.6 (2017-12-06)

- FEATURE: Remote-Procedure-Call (RPC) speedup due to removal of extra pickling step.
- FIX: Added workaround for [CPython issue 24960](https://bugs.python.org/issue24960) (embedded zip file extracted into library folder) - was triggered by latest version of `pluggy` (dependency of `pytest`).
- FIX: Preexisting installation of `wine-python` is now always being removed completely when required due to update or new installation.
- DEV: Moved definition of development dependencies into `setup.py`.

## 0.0.5 (2017-11-13)

* FEATURE: Support for light-weight pointers (`ctypes.byref`)
* FIX: Elements within structures are properly synchronized even if they are not a pointer on their own.
* FIX: Structure objects in arrays of structures are properly initialized.
* FIX: Links in `README.rst` work when rendered on PyPI.

## 0.0.4 (2017-11-05)

- FEATURE: Full support for multidimensional fixed length arrays.

## 0.0.3 (2017-11-02)

- FEATURE: Fixed length 1D arrays.
- DOCS: Lots of typos and grammar issues in documentation fixed.
- DEV: Refactored argument packing and unpacking code.
- DEV: Introduced Python's `any` functions in a number of places.
- DEV: Plenty of cleanups based on static code analysis.

## 0.0.2 (2017-07-28)

- FEATURE: Added and confirmed CPython 3.4 compatibility.
- DOCS: Added installation instructions to documentation.

## 0.0.1 (2017-07-28)

- First official (pre-) release of `zugbruecke`.
