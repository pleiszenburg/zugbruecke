# -*- coding: utf-8 -*-

# Expose session class to user
from .core import session_class as session

# Expose windll and patched ctypes to user
from .core import windll_class
import ctypes
ctypes.windll = windll_class()
