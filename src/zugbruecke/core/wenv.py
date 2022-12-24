# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/wenv.py: Wenv package wrapper

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


import importlib
import os
import shutil
import site
import warnings

import zugbruecke
from wenv import Env as _Env, __version__ as wenv_version

from .typeguard import typechecked


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
def _symlink(src: str, dest: str):

    if os.path.exists(dest) and not os.path.islink(dest):
        warnings.warn(f'"{dest:s}" is exists but not a symlink', RuntimeWarning)
        return

    if not os.path.lexists(dest):
        os.symlink(src, dest)

    if not os.path.exists(dest):
        raise OSError(f'"{dest:s}" could not be created / does not exist')
    if not os.path.islink(dest):
        warnings.warn(f'"{dest:s}" is not a symlink', RuntimeWarning)
    if os.readlink(dest) != src:
        warnings.warn(f'"{dest:s}" points to the wrong source', RuntimeWarning)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


@typechecked
class Env(_Env):
    """
    Represents one Wine Python environment. Derived from ``wenv.Env``. Mutable.

    args:
        kwargs : An arbitrary number of keyword arguments matching valid ``wenv`` configuration options.
    """

    def setup_zugbruecke(self):
        """
        Creates symlinks from ``site-packages`` folder in the *Unix Python* environment
        into the ``site-packages`` folder in the *Windows Python* environment for the following packages:

        - ``zugbruecke``
        - ``wenv``

        Should any of the above packages be updated on the Unix side,
        the update automatically becomes available on the Wine side.
        """

        self._setup_package(name = "zugbruecke", version = zugbruecke.__version__)
        self._setup_package(name = "wenv", version = wenv_version)

    def _setup_package(self, name: str, version: str):

        # Package path in unix-python site-packages
        unix_pkg_path = os.path.abspath(os.path.dirname(importlib.util.find_spec(name).origin))

        # Package path in wine-python site-packages
        wine_pkg_path = os.path.abspath(
            os.path.join(self._path_dict["sitepackages"], name)
        )

        if not self._p["copy_modules"]:
            # Link zugbruecke package into wine-python site-packages
            _symlink(unix_pkg_path, wine_pkg_path)
        else:
            if not os.path.exists(wine_pkg_path):
                # Copy zugbruecke package into wine-python site-packages
                shutil.copytree(unix_pkg_path, wine_pkg_path)

        dist_name = f"{name:s}-{version:s}.dist-info"

        # Dist path in unix-python site-packages
        unix_dist_path = None
        for sitepackages in site.getsitepackages() + [site.getusersitepackages()]:
            if dist_name.lower() not in [item.lower() for item in os.listdir(sitepackages)]:
                continue
            unix_dist_path = os.path.abspath(
                os.path.join(sitepackages, dist_name)
            )
            break
        if unix_dist_path is None:
            raise ValueError('dist-info for package could not be found', name)

        # Dist path in wine-python site-packages
        wine_dist_path = os.path.abspath(
            os.path.join(self._path_dict["sitepackages"], dist_name)
        )

        if not self._p["copy_modules"]:
            # Link zugbruecke dist into wine-python site-packages
            _symlink(unix_dist_path, wine_dist_path)
        else:
            if not os.path.exists(wine_dist_path):
                # Copy zugbruecke dist into wine-python site-packages
                shutil.copytree(unix_dist_path, wine_dist_path)
