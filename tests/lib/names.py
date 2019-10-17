
import os

def get_dll_fn(arch, convention, test_fn, custom = None):
	"get name & path of test dll for given arch and convention"

	assert test_fn.lower().endswith('.py')
	name = test_fn[:-3]

	return '{NAME:s}_{CONVENTION:s}-{ARCH:s}{CUSTOM:s}.dll'.format(
		NAME = name,
		CONVENTION = convention,
		ARCH = arch,
		CUSTOM = ('-' + custom) if custom is not None else '',
		)

def get_dll_path(arch, convention, test_fn, custom = None):
	"get name & path of test dll for given arch and convention RELATIVE TO CWD"

	return os.path.join(
		get_test_fld(abspath = False),
		get_dll_fn(arch, convention, test_fn, custom = custom),
		)

def get_test_fld(abspath = True):
	"get full path of project test folder"

	cwd = os.path.abspath(os.getcwd())
	test_fld = None

	if not os.path.isfile('setup.cfg'):
		raise FileNotFoundError('setup.cfg configuration file missing in cwd')

	with open('setup.cfg', 'r', encoding = 'utf-8') as f:
		for line in f:
			if not 'testpaths = ' in line:
				continue
			test_fld = line.split(' = ', 1)[1].strip()
			break

	if test_fld is None:
		raise ValueError('setup.cfg does not contain "testpaths" information')

	if abspath:
		test_fld = os.path.join(cwd, test_fld)

	if not os.path.isdir(test_fld):
		raise ValueError('"testpaths" in setup.cfg does not point to an existing directory')

	return test_fld
