class CDLL(object):
	"""
	An instance of this class represents a loaded dll/shared
	library, exporting functions using the standard C calling
	convention (named 'cdecl' on Windows).
	The exported functions can be accessed as attributes, or by
	indexing with the function name.  Examples:
	<obj>.qsort -> callable object
	<obj>['qsort'] -> callable object
	Calling the functions releases the Python GIL during the call and
	reacquires it afterwards.
	"""


	_func_flags_ = _FUNCFLAG_CDECL
	_func_restype_ = c_int
	# default values for repr
	_name = '<uninitialized>'
	_handle = 0
	_FuncPtr = None


	def __init__(
		self, name, mode = DEFAULT_MODE, handle = None,
		use_errno = False,
		use_last_error = False
		):

		self._name = name
		flags = self._func_flags_
		if use_errno:
			flags |= _FUNCFLAG_USE_ERRNO
		if use_last_error:
			flags |= _FUNCFLAG_USE_LASTERROR

		class _FuncPtr(_CFuncPtr):
			_flags_ = flags
			_restype_ = self._func_restype_
		self._FuncPtr = _FuncPtr

		if handle is None:
			self._handle = _dlopen(self._name, mode)
		else:
			self._handle = handle

	def __repr__(self):

		return "<%s '%s', handle %x at %#x>" % \
			(self.__class__.__name__, self._name,
			(self._handle & (_sys.maxsize*2 + 1)),
			id(self) & (_sys.maxsize*2 + 1))


	def __getattr__(self, name):

		if name.startswith('__') and name.endswith('__'):
			raise AttributeError(name)
		func = self.__getitem__(name)
		setattr(self, name, func)
		return func


	def __getitem__(self, name_or_ordinal):

		func = self._FuncPtr((name_or_ordinal, self))
		if not isinstance(name_or_ordinal, int):
			func.__name__ = name_or_ordinal
		return func
