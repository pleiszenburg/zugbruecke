# -*- coding: utf-8 -*-

# Load windll_class for minicing ctypes.windll eventually, make it private
from .core import windll_class as __windll_class__

# Set up and expose windll, starting session while doing so
windll = __windll_class__()

# Import and expose ctypes
import ctypes

# Patching ctypes
ctypes.windll = windll

# Exposing LoadLibrary from running session for direct import
LoadLibrary = windll.LoadLibrary

# Expose session class for advanced users and tests
from .core import session_class as session
