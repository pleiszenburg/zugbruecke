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

from .. import __version__ as zugbruecke_version
from wenv import __version__ as wenv_version

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
    Represents one Wine Python environment. Derived from ``wenv.Env``. Mutable.

    args:
        kwargs : An arbitrary number of keyword arguments matching valid ``wenv`` configuration options.
    """

    _zugbruecke_version = zugbruecke_version
    _wenv_version = wenv_version

    def setup_zugbruecke(self):
        """
        Creates symlinks from ``site-packages`` folder in the *Unix Python* environment
        into the ``site-packages`` folder in the *Windows Python* environment for the following packages:

        - ``zugbruecke``
        - ``wenv``

        Should any of the above packages be updated on the Unix side,
        the update automatically becomes available on the Wine side.
        """

        self._setup_package(name = "zugbruecke", version=Env._zugbruecke_version)
        self._setup_package(name = "wenv", version=Env._wenv_version)

    def _setup_package(self, name: str, version: str=""):

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

        # Egg or dist path in unix-python and in wine-python site-packages
        unix_meta_path = os.path.abspath(
            os.path.join(unix_pkg_path, "..", f"{name:s}.egg-info")
        )
        if os.path.exists(unix_meta_path):
            # egg path
            wine_meta_path = os.path.abspath(
                os.path.join(self._path_dict["sitepackages"], f"{name:s}.egg-info")
            )
        else:
            # dist path
            unix_meta_path = os.path.abspath(
                os.path.join(unix_pkg_path, "..", f"{name:s}-{version:s}.dist-info")
            )
            wine_meta_path = os.path.abspath(
                os.path.join(self._path_dict["sitepackages"], f"{name:s}-{version:s}.dist-info")
            )
        if not self._p["_issues_50_workaround"]:
            # Link zugbruecke egg or dist into wine-python site-packages
            _symlink(unix_meta_path, wine_meta_path)
        else:
            if not os.path.exists(wine_meta_path):
                # Copy zugbruecke egg or dist into wine-python site-packages
                shutil.copytree(unix_meta_path, wine_meta_path)
