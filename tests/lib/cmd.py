# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/cmd.py: Thin wrapper around subprocess.Popen

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
from typing import Dict, List, Optional

from typeguard import typechecked

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def run_cmd(cmd: List[str], env: Optional[Dict[str, str]] = None):
    """
    Minimal subprocess.Popen wrapper

    Args:
        - cmd: List of command fragments for Popen
        - env: Environment variables
    """

    envvars = os.environ.copy()
    if env is not None:
        envvars.update(env)

    # for name in ('PWD', 'OLDPWD', 'VIRTUAL_ENV', 'PYTHONPATH'):
    #     try:
    #         envvars.pop(name)
    #     except KeyError:
    #         continue

    # print('???', envvars)

    proc = Popen(cmd, env = envvars)
    proc.wait()
    if proc.returncode != 0:
        raise SystemError('command failed', cmd, env)
