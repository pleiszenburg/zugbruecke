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
import importlib
from json import dumps, loads
import os
from platform import architecture, release
from pprint import pformat as pf
from subprocess import Popen, PIPE
import sys
from time import time_ns
from typing import Any, Callable, Dict, List

from typeguard import typechecked
from wenv import EnvConfig, PythonVersion

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

                func_handle = initializer(
                    ctypes = ctypes,
                    dll_handle = dll_handle,
                    conv = convention,
                )
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
                    name = func.__name__,
                    runtime = min_runtime,
                    runs = counter,
                    server = server,
                    client = sys.version.split(' ')[0],
                )
                reports.append(report)

                print(pf(report))

            return reports

        inner.is_benchmark = None
        return inner

    return outer


@typechecked
def _get_benchmarks() -> List[Callable]:
    """
    auto-detects benchmarks
    """

    benchmarks = []

    for item in os.listdir('benchmark'):

        if item.startswith("_") or not item.lower().endswith(".py"):
            continue

        try:
            mod = importlib.import_module(f"benchmark.{item[:-3]:s}")
        except ModuleNotFoundError:  # likely no gui support
            continue

        for attr in dir(mod):
            entry = getattr(mod, attr)
            if not hasattr(entry, 'is_benchmark'):
                continue
            benchmarks.append(entry)

    return benchmarks


@typechecked
def _group_data(data: List) -> Dict:
    """
    Group parsed raw data by benchmark, arch, version and calling convention
    """

    by_benchmark = {}
    for entry in data:
        name = entry['name']
        try:
            group = by_benchmark[name]
        except KeyError:
            group = []
            by_benchmark[name] = group
        group.append(entry)

    by_archverconv = {name: {} for name in by_benchmark.keys()}
    for name, group in by_benchmark.items():
        for entry in group:
            archver = (
                entry['server'] if entry['server'] is not None else entry['client'],
                entry['arch'],
                entry['convention']
            )
            try:
                subgroup = by_archverconv[name][archver]
            except KeyError:
                subgroup = []
                by_archverconv[name][archver] = subgroup
            subgroup.append(entry)

    return by_archverconv


@typechecked
def _make_table(name: str, group: Dict, doc: str):
    """
    Write on RST table from parsed and grouped data
    """

    keys = sorted(
        group.keys(),
        key = (lambda item: (PythonVersion.from_config(item[1], item[0]), item[1], item[2])),
    )

    with open(os.path.join('docs', 'source', f'benchmark_{name}.rst'), mode = 'w', encoding="utf-8") as f:

        f.write(f'.. csv-table:: "{name:s}" benchmark, CPython {sys.version.split(" ")[0]:s} on {sys.platform:s}, versions of CPython on Wine\n')
        f.write('    :header: "version", "arch", "convention", "ctypes [µs]", "zugbruecke [µs]", "overhead [µs]"\n')
        f.write('    :delim: 0x0003B\n')
        f.write('\n')

        for version, arch, conv in keys:
            unix, wine = group[(version, arch, conv)]
            if unix['server'] is None:
                unix, wine = wine, unix
            unix, wine = round(unix['runtime'] / 1e3, 1), round(wine['runtime'] / 1e3, 1)
            f.write(f'    "{version:s}"; "{arch:s}"; "{conv:s}"; {wine:,.01f}; {unix:,.01f}; {unix-wine:,.01f}\n')

        f.write('\n')
        for line in doc.split('\n'):
            f.write(f'{line[4:]:s}\n')


@typechecked
def _make_inventory(names: List[str]):

    with open(os.path.join('docs', 'source', 'benchmarks_all.rst'), mode = 'w', encoding="utf-8") as f:
        for name in names:
            f.write(f'.. include:: benchmark_{name:s}.rst\n')


def _make_sysinfo():

    with open('/proc/cpuinfo', mode='r', encoding='utf-8') as f:
        cpuinfo = f.read()
    cpuinfo = [line for line in cpuinfo.split('\n') if 'model name' in line][0].split(':')[1].strip()

    proc = Popen(['wine', '--version'], stdout = PIPE)
    wine, _ = proc.communicate()
    wine = wine.decode('utf-8').strip().split('-')[1]

    with open(os.path.join('docs', 'source', 'benchmarks_sysinfo.rst'), mode = 'w', encoding="utf-8") as f:
        f.write('Benchmarks were performed on an ')
        f.write(f'"{cpuinfo:s}" CPU, ')
        f.write(f'Linux {release():s} {architecture()[0]}, ')
        f.write(f'and Wine {wine:s}')
        f.write('.\n')


def _make_tables():
    """
    Write RST table from raw benchmark data
    """

    benchmarks = {
        entry.__name__: entry.__doc__
        for entry in _get_benchmarks()
    }

    data = []
    with open(os.path.join('benchmark', 'data.raw'), mode = 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if len(line) == 0:
                continue
            data.extend(loads(line))

    for name, group in _group_data(data).items():
        _make_table(name, group, benchmarks[name])

    _make_inventory(list(benchmarks.keys()))
    _make_sysinfo()


def _run_wenv():
    """
    Run benchmarks on Wine from Unix
    """

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


def main():
    """
    Run all benchmarks both on Unix and Wine
    """

    if len(sys.argv) > 1 and sys.argv[1] == 'wine':
        _run_wenv()
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'table':
        _make_tables()
        return
    if len(sys.argv) > 1 and sys.argv[1] != 'unix':
        raise SystemError(f'unknown parameter "{sys.argv[1]:s}"')

    fn = os.path.join('benchmark', 'data.raw')

    if not os.path.exists(fn):
        with open(fn, mode = 'w', encoding='utf-8') as f:
            f.write("")

    for item in _get_benchmarks():
        reports = item()
        with open(fn, mode = "a", encoding='utf-8') as f:
            f.write(f'{dumps(reports):s}\n')


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    main()
