# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/data/core.py: Central data handler per side and session

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

from typing import Optional

from .arg_contents import ArgContents
from .arg_definition import arguments_definition_class
from .mem_definition import memory_definition_class

from ..abc import CacheABC, DataABC, LogABC, RpcClientABC, RpcServerABC
from ..typeguard import typechecked

from .cache import Cache


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASS
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

@typechecked
class Data(
    DataABC,
    ArgContents,
    arguments_definition_class,
    memory_definition_class,
):
    """
    Handles argument definitions, contents and memory sync
    """

    def __init__(
        self,
        log: LogABC,
        is_server: bool,
        callback_client: Optional[RpcClientABC] = None,
        callback_server: Optional[RpcServerABC] = None,
    ):

        self._log = log
        self._is_server = is_server

        self._callback_client = callback_client
        self._callback_server = callback_server

        self._cache = Cache()

    @property
    def cache(self) -> CacheABC:

        return self._cache
