# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/run.py: Test runner

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

import os
from subprocess import Popen
import sys
from typing import Dict, List, Optional

from wenv import EnvConfig

from .const import PYTHONBUILDS_FN
from .pythonversion import read_python_builds

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def run_tests():
    """
    Dispatcher: Wine/Unix
    """

    if len(sys.argv) < 2:
        raise SystemError('expected at least 2 arguments, got other', len(sys.argv))

    target = sys.argv[1]

    if target == 'wine':
        _run_tests_wine(*sys.argv[2:])
    elif target == 'unix':
        _run_tests_unix(*sys.argv[2:])
    else:
        raise SystemError('unknown test target', target)


def _run_tests_wine(*args: str):
    """
    Runs test suite on Wine as if it was running on Windows,
    i.e. testing & verifying against original ctypes.
    No coverage recorded.
    """

    cfg = EnvConfig()
    builds = read_python_builds(fn = os.path.join(cfg['prefix'], PYTHONBUILDS_FN))

    for arch, _builds in builds.items():
        for build in _builds:
            _run(
                cmd = ['make', '_clean_py'],
            )
            _run(
                cmd = ['wenv', 'pytest', '--hypothesis-show-statistics', *args],
                env = {
                    'WENV_DEBUG': '1',
                    'WENV_ARCH': arch,
                    'WENV_PYTHONVERSION': str(build),
                },
            )


def _run_tests_unix(*args: str):
    """
    Does a single run of pytest. ARCH and PYTHONVERSION are parameterized within pytest.
    """

    _run(
        cmd = ['make', '_clean_py'],
    )
    _run(
        cmd = [
            'pytest',
            '--cov=zugbruecke',
            # '--cov-config=setup.cfg',
            '--hypothesis-show-statistics',
            # '--capture=no',
            *args,
        ],
        env = {
            'WENV_DEBUG': '1',
            'ZUGBRUECKE_DEBUG': '1',
            'ZUGBRUECKE_LOG_LEVEL': '100',
        },
    )


def _run(cmd: List[str], env: Optional[Dict[str, str]] = None):

    envvars = os.environ.copy()
    if env is not None:
        envvars.update(env)

    proc = Popen(cmd, env = envvars)
    proc.wait()
    if proc.returncode != 0:
        raise SystemError('test command failed', cmd, env)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    run_tests()
