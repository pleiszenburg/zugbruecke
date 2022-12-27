# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/pythonversion.py: IO for wenv's PythonVersion class

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

from json import dumps, loads
from typing import Dict, List

from typeguard import typechecked
from wenv import PythonVersion

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def read_python_builds(fn: str) -> Dict[str, List[PythonVersion]]:
    """
    Read JSON file containing list of installed Windows Python builds

    Args:
        - fn: Location of JSON file
    Returns:
        Available Windows Python builds in Wine Python environments
    """

    with open(fn, mode = "r", encoding="utf-8") as f:
        raw = f.read()

    return {
        arch: [PythonVersion.from_config(arch, build) for build in builds]
        for arch, builds in loads(raw).items()
    }


@typechecked
def write_python_builds(fn: str, builds: Dict[str, List[PythonVersion]]):
    """
    Read JSON file containing list of installed Windows Python builds

    Args:
        - Available Windows Python builds in Wine Python environments
    """

    with open(fn, mode = "w", encoding="utf-8") as f:
        f.write(dumps({
            arch: [
                build.as_config() for build in _builds
            ] for arch, _builds in builds.items()
        }))
