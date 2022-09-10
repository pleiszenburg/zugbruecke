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
import tempfile

from jinja2 import Template

from .const import (
    ARCHS,
    CONVENTIONS,
    CC,
    CFLAGS,
    LDFLAGS,
    DLL_FLD,
    DLL_HEADER,
    DLL_SOURCE,
    PREFIX,
    SUFFIX,
)
from .names import get_dll_fn, get_test_fld
from .parser import get_vars_from_source

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_header_and_source_from_test(fn):
    "extract header and source from Python test file without importing it"

    with open(fn, "r", encoding="utf-8") as f:
        src = f.read()

    var_dict = get_vars_from_source(src, "HEADER", "SOURCE", "EXTRA")

    return var_dict["HEADER"], var_dict["SOURCE"], var_dict["EXTRA"]


def get_testfn_list(test_fld):
    "get list of Python test files in project test folder"

    testfn_list = []

    for entry in os.listdir(test_fld):
        if not entry.lower().endswith(".py"):
            continue
        if not entry.lower().startswith("test_"):
            continue
        if not os.path.isfile(os.path.join(test_fld, entry)):
            continue
        testfn_list.append(entry)

    return testfn_list


def make_all():

    test_fld = get_test_fld()
    test_fn_list = get_testfn_list(test_fld)

    jobs = []

    for test_fn in test_fn_list:

        header, source, extra = get_header_and_source_from_test(
            os.path.join(test_fld, test_fn)
        )
        if header is None:
            print('test "%s" does not contain a C HEADER - ignoring' % test_fn)
            continue
        if source is None:
            print('test "%s" does not contain C SOURCE - ignoring' % test_fn)
            continue

        for convention in CONVENTIONS:
            for arch in ARCHS:
                jobs.append(
                    (test_fld, arch, convention, test_fn, header, source, extra)
                )

    with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
        _ = p.map(make_dll, jobs)


def make_dll(param):
    "compile test dll"

    test_fld, arch, convention, test_fn, header, source, extra = param

    if extra is None:
        extra = dict()

    HEADER_FN = "tmp_header.h"
    SOURCE_FN = "tmp_source.c"

    build_fld = tempfile.mkdtemp()

    dll_fn = get_dll_fn(arch, convention, test_fn)
    dll_test_path = os.path.join(test_fld, DLL_FLD, dll_fn)
    dll_build_path = os.path.join(build_fld, dll_fn)
    header_path = os.path.join(build_fld, HEADER_FN)
    source_path = os.path.join(build_fld, SOURCE_FN)

    print('Building "{DLL_FN:s}" ... '.format(DLL_FN=dll_fn), end="")

    with open(header_path, "w", encoding="utf-8") as f:
        f.write(
            Template(DLL_HEADER).render(
                HEADER=Template(header).render(
                    PREFIX=PREFIX[convention], SUFFIX=SUFFIX[convention], **extra
                ),
            )
        )
    with open(source_path, "w", encoding="utf-8") as f:
        f.write(
            Template(DLL_SOURCE).render(
                HEADER_FN=HEADER_FN,
                SOURCE=Template(source).render(
                    PREFIX=PREFIX[convention], SUFFIX=SUFFIX[convention], **extra
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

    shutil.move(dll_build_path, dll_test_path)
    if not os.path.isfile(dll_test_path):
        raise SystemError("dll file was not moved from build directory")

    shutil.rmtree(build_fld)

    print("done.")


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    make_all()
