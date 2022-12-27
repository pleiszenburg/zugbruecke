# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/install.py: Sets Wine Python environments up

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

import os
from subprocess import Popen
from typing import Dict, List

from toml import loads
from typeguard import typechecked

from zugbruecke import Config, Env

from wenv import (
    EnvConfig,
    PythonVersion,
    get_available_python_builds,
    get_latest_python_build,
)

from .const import (
    ARCHS,
    PYTHONBUILDS_FN,
    PYTHON_MINOR_MAX,
    PYTHON_MINOR_MIN,
)
from .pythonversion import write_python_builds

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def install():
    """
    Create all required Wine Python environments for testing
    """

    cfg = EnvConfig()
    builds = _get_latest_python_builds()

    write_python_builds(fn = os.path.join(cfg['prefix'], PYTHONBUILDS_FN), builds = builds)

    for arch in ARCHS:
        for build in builds[arch]:
            _install_env(arch, build)


@typechecked
def _get_latest_python_builds() -> Dict[str, List[PythonVersion]]:
    """
    Create a list per architecture of the latest Python maintenance release per minor version
    """

    _builds = get_available_python_builds()

    builds = {
        arch: [
            get_latest_python_build(arch, 3, minor, builds = _builds)
            for minor in range(
                PYTHON_MINOR_MIN,  # min minor version
                PYTHON_MINOR_MAX + 1,  # max major version
            )
        ]
        for arch in ARCHS
    }
    for value in builds.values():
        value.sort()

    return builds


@typechecked
def _install_env(arch: str, build: PythonVersion):
    """
    Create a Wine Python environment

    Args:
        - arch: Architecture
        - build: Python version
    """

    print(f'<INSTALLING WENV PYTHON {str(build).upper()} ON {arch.upper():s}>')

    envvars = os.environ.copy()
    envvars.update({
        'WENV_DEBUG': '1',
        'WENV_ARCH': arch,
        'WENV_PYTHONVERSION': str(build),
    })

    with open('pyproject.toml', mode = 'r', encoding = 'utf-8') as f:
        pyproject = loads(f.read())

    for cmd in (
        ['wenv', 'init'],
        ['wenv', 'pip', 'install'] + pyproject['project']['optional-dependencies']['test'],
        ['wenv', 'init_coverage'],
    ):
        proc = Popen(cmd, env = envvars)
        proc.wait()
        if proc.returncode != 0:
            raise SystemError('wenv setup command failed', arch, build, cmd)

    env = Env(**EnvConfig(
        arch = arch,
        pythonversion = build,
        copy_modules = Config()['copy_modules'],  # pass option on
    ).export_dict())
    env.setup_zugbruecke() # link packages to wenv python environment


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# MODULE ENTRY POINT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    install()
