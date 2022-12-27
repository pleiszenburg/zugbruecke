# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    src/zugbruecke/core/abc.py: Abstract base classes

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

from abc import ABC

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# CLASSES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class CacheABC(ABC):
    pass


class CallbackClientABC(ABC):
    pass


class CallbackServerABC(ABC):
    pass


class ConfigABC(ABC):
    pass


class CtypesSessionABC(ABC):
    pass


class DataABC(ABC):
    pass


class DefinitionABC(ABC):
    pass


class DefinitionMemsyncABC(ABC):
    pass


class DllClientABC(ABC):
    pass


class DllServerABC(ABC):
    pass


class InterpreterABC(ABC):
    pass


class LogABC(ABC):
    pass


class MempkgABC(ABC):
    pass


class MessageABC(ABC):
    pass


class RoutineClientABC(ABC):
    pass


class RoutineServerABC(ABC):
    pass


class RpcClientABC(ABC):
    pass


class RpcServerABC(ABC):
    pass


class SessionClientABC(ABC):
    pass


class SessionServerABC(ABC):
    pass
