#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    run_test.py: Run one individual test

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

import argparse
import importlib
import os
import sys
import traceback


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CONST
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

ZB_CONFIG_FN = ".zugbruecke.json"


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES AND ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def run_test(test_module, test_routine):

    cwd = os.path.dirname(os.path.abspath(__file__))

    test_fld = None
    with open("setup.cfg", "r") as f:
        for line in f:
            if not "testpaths = " in line:
                continue
            test_fld = line.split(" = ", 1)[1].strip()
            break
    if test_fld is None:
        raise  # TODO
    if not os.path.isdir(os.path.join(cwd, test_fld)):
        raise  # TODO

    sys.path.append(os.path.join(cwd, test_fld))

    getattr(importlib.import_module(test_module), test_routine)()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# INIT
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--module", type=str, nargs=1)
    parser.add_argument("-r", "--routine", type=str, nargs=1)
    args = parser.parse_args()

    try:
        run_test(args.module[0], args.routine[0])
    except:
        traceback.print_exc()
