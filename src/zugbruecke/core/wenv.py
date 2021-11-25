# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/wenv.py: Wenv package wrapper

    Required to run on platform / side: [UNIX]

    Copyright (C) 2017-2021 Sebastian M. Ernst <ernst@pleiszenburg.de>

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

import importlib
import os
import shutil

from wenv import Env as _Env

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def _symlink(src, dest):

    if not os.path.lexists(dest):
        os.symlink(src, dest)

    if not os.path.exists(dest):
        raise OSError('"{LINK:s}" could not be created'.format(LINK=dest))
    if not os.path.islink(dest):
        raise OSError('"{LINK:s}" is not a symlink'.format(LINK=dest))
    if os.readlink(dest) != src:
        raise OSError('"{LINK:s}" points to the wrong source'.format(LINK=dest))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Env(_Env):
    """
    Wine Python environment
    """

    def setup_zugbruecke(self):

        self._setup_package(name = "zugbruecke")
        self._setup_package(name = "wenv")

    def _setup_package(self, name: str):

        # Package path in unix-python site-packages
        unix_pkg_path = os.path.abspath(os.path.dirname(importlib.util.find_spec(name).origin))

        # Package path in wine-python site-packages
        wine_pkg_path = os.path.abspath(
            os.path.join(self._path_dict["sitepackages"], name)
        )

        if not self._p["_issues_50_workaround"]:
            # Link zugbruecke package into wine-python site-packages
            _symlink(unix_pkg_path, wine_pkg_path)
        else:
            if not os.path.exists(wine_pkg_path):
                # Copy zugbruecke package into wine-python site-packages
                shutil.copytree(unix_pkg_path, wine_pkg_path)

        # Egg path in unix-python site-packages
        unix_egg_path = os.path.abspath(
            os.path.join(unix_pkg_path, "..", f"{name:s}.egg-info")
        )
        # Egg path in wine-python site-packages
        wine_egg_path = os.path.abspath(
            os.path.join(self._path_dict["sitepackages"], f"{name:s}.egg-info")
        )

        if not self._p["_issues_50_workaround"]:
            # Link zugbruecke egg into wine-python site-packages
            _symlink(unix_egg_path, wine_egg_path)
        else:
            if not os.path.exists(wine_egg_path):
                # Copy zugbruecke egg into wine-python site-packages
                shutil.copytree(unix_egg_path, wine_egg_path)
