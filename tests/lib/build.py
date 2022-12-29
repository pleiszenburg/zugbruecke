# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/build.py: Build DLLs from templates

    Required to run on platform / side: [UNIX]

    Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>

<LICENSE_BLOCK>
The contents of this file are subject to the GNU Lesser General Public License
Version 2.1 ("LGPL" or "License"). You may not use this file except in
compliance with the License. You may obtain a copy of the License at
https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE

Software distributed under the License is distributed on an "AS IS" basis,
WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
specific language governing rights and limitations under the License.
</LICENSE_BLOCK>

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# IMPORT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Optional, Tuple

from jinja2 import Template
from typeguard import typechecked

from .const import (
    ARCHS,
    CONVENTIONS,
    CC,
    CFLAGS,
    HEADER_FN,
    LDFLAGS,
    DLL_FLD,
    DLL_HEADER,
    DLL_SOURCE,
    PREFIX,
    SUFFIX,
    SOURCE_FN,
)
from .names import (
    get_dll_fn,
    get_benchmark_fld,
    get_benchmark_fns,
    get_test_fld,
    get_test_fns,
)
from .parser import get_vars_from_source

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def get_header_and_source_from_test(fn: str) -> Tuple[Optional[str], Optional[str], Optional[Any]]:
    """
    extract header and source from Python test file without importing it

    Args:
        - fn: File name / path of Python code file
    Returns:
        Tuple of header, source and extra strings
    """

    with open(fn, "r", encoding="utf-8") as f:
        src = f.read()

    variables = get_vars_from_source(src, "HEADER", "SOURCE", "EXTRA")

    return variables["HEADER"], variables["SOURCE"], variables["EXTRA"]


def make_all():
    """
    Build all DLLs C code templates in Python files in given folder
    """

    group = sys.argv[1]
    assert group in ('tests', 'benchmark')

    if group == 'tests':
        fld = get_test_fld()
        fns = get_test_fns(fld)
    elif group == 'benchmark':
        fld = get_benchmark_fld()
        fns = get_benchmark_fns(fld)
    else:
        raise ValueError(f'unknown group of DLLs "{group:s}"')

    jobs = []

    for fn in fns:

        header, source, extra = get_header_and_source_from_test(
            os.path.join(fld, fn)
        )
        if header is None:
            print(f'test "{fn:s}" does not contain a C HEADER - ignoring')
            continue
        if source is None:
            print(f'test "{fn:s}" does not contain C SOURCE - ignoring')
            continue

        for convention in CONVENTIONS:
            for arch in ARCHS:
                jobs.append(
                    (fld, fn, arch, convention, header, source, extra)
                )

    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        _ = p.map(make_dll_wrapper, jobs)


@typechecked
def make_dll_wrapper(params: Tuple):
    """
    Wrapper for argument unpacking in multiprocessing
    """

    make_dll(*params)


@typechecked
def make_dll(
    fld: str,
    fn: str,
    arch: str,
    convention: str,
    header: str,
    source: str,
    extra: Optional[Any] = None,
):
    """
    compile DLL from fragments

    Args:
        - fld: Location of Python source code file
        - fn: Name of Python source code file
        - arch: Architecture
        - convention: Calling convention
        - header: C header template
        - source: C source template
        - extra: Additional parameters for template engine
    """

    if extra is None:
        extra = dict()

    build_fld = tempfile.mkdtemp()

    dll_fn = get_dll_fn(arch, convention, fn)

    dll_build_path = os.path.join(build_fld, dll_fn)
    dll_deploy_path = os.path.join(fld, DLL_FLD, dll_fn)
    header_path = os.path.join(build_fld, HEADER_FN)
    source_path = os.path.join(build_fld, SOURCE_FN)

    print(f'Building "{dll_fn:s}" ... ', end = '')

    with open(header_path, "w", encoding="utf-8") as f:
        f.write(
            Template(DLL_HEADER).render(
                HEADER=Template(header).render(
                    PREFIX=PREFIX[convention], SUFFIX=SUFFIX[convention], ARCH = arch, **extra,
                ),
            )
        )
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(
            Template(DLL_SOURCE).render(
                HEADER_FN=HEADER_FN,
                SOURCE=Template(source).render(
                    PREFIX=PREFIX[convention], SUFFIX=SUFFIX[convention], ARCH = arch, **extra
                ),
            )
        )

    proc = subprocess.Popen(
        [CC[arch], source_path] + CFLAGS[convention] + ["-o", dll_build_path] + LDFLAGS,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise SystemError(
            "compiler exited with error, returncode %d" % proc.returncode,
            out.decode("utf-8"),
            err.decode("utf-8"),
        )
    if not os.path.isfile(dll_build_path):
        raise SystemError(
            "no compiler error but also no dll file present",
            out.decode("utf-8"),
            err.decode("utf-8"),
        )

    shutil.move(dll_build_path, dll_deploy_path)
    if not os.path.isfile(dll_deploy_path):
        raise SystemError("dll file was not moved from build directory")

    shutil.rmtree(build_fld)

    print("done.")


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    make_all()
