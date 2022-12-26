# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/benchmark.py: Benchmark decorator (archs / Python versions / calling conventions)

    Required to run on platform / side: [UNIX, WINE]

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

from functools import wraps
from pprint import pformat as pf
import os
import sys
from time import time_ns
from typing import Any, Callable, Dict, List

from typeguard import typechecked
from wenv import EnvConfig

from .cmd import run_cmd
from .const import ARCHITECTURE, ARCHS, CONVENTIONS, PLATFORM, PYTHONBUILDS_FN
from .names import get_benchmark_fld
from .pythonversion import read_python_builds

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def _permutations(fn: str):
    """
    Provides all permutations on calling convention, arch, ctypes/Python version

    Args:
        - fn: File name of Python source file
    Yields:
        Tuple containing arch, convention, ctypes, dll handle
    """

    from .ctypes import CTYPES, get_dll_handle

    fn = os.path.basename(fn)
    fld = get_benchmark_fld()

    for convention in CONVENTIONS:
        for arch in ARCHS:
            for ctypes_build in CTYPES.get(arch, tuple()):
                if PLATFORM == "unix" or arch[3:] == ARCHITECTURE:
                    yield (
                        arch,
                        convention,
                        ctypes_build,
                        get_dll_handle(
                            arch,
                            ctypes_build,
                            convention,
                            fld,
                            fn,
                        ),
                    )


@typechecked
def benchmark(fn: str, initializer: Callable) -> Any:
    """
    Decorator for benchmark functions

    Args:
        - fn: File name of Python source file
    Yields:
        DLL handles per calling convention, architecture and wenv Python version
    """

    def outer(func: Callable) -> Callable:

        @wraps(func)
        def inner() -> List[Dict]:

            reports = []

            for arch, convention, ctypes, dll_handle in _permutations(fn):

                print(f'Benchmark ...')

                func_handle = initializer(ctypes, dll_handle)
                min_runtime = None
                benchmark_start = time_ns()
                counter = 0

                while 1_000_000_000 > time_ns() - benchmark_start:  # at least one sec

                    iteration_start = time_ns()

                    func(ctypes, func_handle)

                    runtime = time_ns() - iteration_start
                    if min_runtime is None or min_runtime > runtime:
                        min_runtime = runtime

                    counter += 1

                server = None
                if PLATFORM == 'unix':
                    server = '.'.join(str(ctypes.zb_get_parameter('pythonversion')).split('.')[:3])

                report = dict(
                    platform = PLATFORM,
                    arch = arch,
                    convention = convention,
                    benchmark = func.__name__,
                    runtime = min_runtime,
                    runs = counter,
                    server = server,
                    client = sys.version.split(' ')[0],
                )
                reports.append(report)

                print(pf(report))

            return report

        inner.is_benchmark = None
        return inner

    return outer


def run_all():
    """
    Run all benchmarks both on Unix and Wine
    """

    if len(sys.argv) > 1 and sys.argv[1] == 'wine':

        cfg = EnvConfig()
        builds = read_python_builds(fn = os.path.join(cfg['prefix'], PYTHONBUILDS_FN))

        for arch, _builds in builds.items():
            for build in _builds:
                run_cmd(
                    cmd = ['make', '_clean_py'],
                )
                run_cmd(
                    cmd = [
                        'wenv', 'python', '-m', 'tests.lib.benchmark'
                    ],
                    env = {
                        'WENV_DEBUG': '0',
                        'WENV_ARCH': arch,
                        'WENV_PYTHONVERSION': str(build),
                        'WENV_NO_PTH_FILE': 'true' if build.minor >= 11 else 'false',  # CPython PR #31542
                    },
                )
        run_cmd(
            cmd = ['make', '_clean_py'],
        )
        return

    elif len(sys.argv) > 1 and sys.argv[1] != 'unix':

        raise SystemError(f'unknown platform "{sys.argv[1]:s}"')

    print('running on', sys.platform, sys.version)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    run_all()
