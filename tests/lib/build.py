
import os
import shutil
import subprocess
import tempfile

from jinja2 import Template

from .const import (
	CC,
	CFLAGS,
	LDFLAGS,
	WINDLL_HEADER,
	WINDLL_SOURCE,
	)
from .parser import get_vars_from_source

def get_header_and_source_from_test(fn):
	"extract header and source from Python test file without importing it"

	with open(fn, 'r', encoding = 'utf-8') as f:
		src = f.read()

	var_dict = get_vars_from_source(src, 'HEADER', 'SOURCE')

	return var_dict['HEADER'], var_dict['SOURCE']

def get_dll_handle(arch, convention, test_fn):
	"get handle to dll for given arch and convention"

	pass

def get_dll_fn(arch, convention, test_fn, custom = None):
	"get name & path of test dll for given arch and convention"

	assert test_fn.lower().endswith('.py')
	name = test_fn[:-3]

	return '{NAME:s}-{CONVENTION:s}-{ARCH:s}{CUSTOM:s}.dll'.format(
		NAME = name,
		CONVENTION = convention,
		ARCH = arch,
		CUSTOM = ('-' + custom) if custom is not None else '',
		)

def get_dll_path(arch, convention, test_fn):
	"get name & path of test dll for given arch and convention RELATIVE TO CWD"

	pass # TODO use get_dll_fn

def get_testfn_list(test_fld):
	"get list of Python test files in project test folder"

	testfn_list = []

	for entry in os.listdir(test_fld):
		if not entry.lower().endswith('.py'):
			continue
		if not entry.lower().startswith('test_'):
			continue
		if not os.path.isfile(os.path.join(test_fld, entry)):
			continue
		testfn_list.append(entry)

	return testfn_list

def get_test_fld():
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

	test_fld = os.path.join(cwd, test_fld)

	if not os.path.isdir(test_fld):
		raise ValueError('"testpaths" in setup.cfg does not point to an existing directory')

	return test_fld

def make_all():

	test_fld = get_test_fld()
	test_fn_list = get_testfn_list(test_fld)
	arch_list = sorted(CC.keys())

	for test_fn in test_fn_list:

		header, source = get_header_and_source_from_test(os.path.join(test_fld, test_fn))
		if header is None:
			print('test "%s" does not contain a C HEADER - ignoring' % test_fn)
			continue
		if source is None:
			print('test "%s" does not contain C SOURCE - ignoring' % test_fn)
			continue

		for arch in arch_list:
			make_dll(test_fld, arch, 'windll', test_fn, header, source) # TODO permutations

def make_dll(test_fld, arch, convention, test_fn, header, source):
	"compile test dll"

	HEADER_FN = 'tmp_header.h'
	SOURCE_FN = 'tmp_source.c'

	build_fld = tempfile.mkdtemp()

	dll_fn = get_dll_fn(arch, convention, test_fn)
	dll_test_path = os.path.join(test_fld, dll_fn)
	dll_build_path = os.path.join(build_fld, dll_fn)
	header_path = os.path.join(build_fld, HEADER_FN)
	source_path = os.path.join(build_fld, SOURCE_FN)

	with open(header_path, 'w', encoding = 'utf-8') as f:
		f.write(Template(WINDLL_HEADER).render(
			HEADER = header,
			))
	with open(source_path, 'w', encoding = 'utf-8') as f:
		f.write(Template(WINDLL_SOURCE).render(
			HEADER_FN = HEADER_FN,
			SOURCE = source,
			))

	proc = subprocess.Popen([
		CC[arch], source_path, *CFLAGS, '-o', dll_build_path, *LDFLAGS
		], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
	out, err = proc.communicate()
	if proc.returncode != 0:
		raise SystemError(
			'compiler exited with error, returncode %d' % proc.returncode,
			out.decode('utf-8'), err.decode('utf-8')
			)
	if not os.path.isfile(dll_build_path):
		raise SystemError(
			'no compiler error but also no dll file present',
			out.decode('utf-8'), err.decode('utf-8')
			)

	shutil.move(dll_build_path, dll_test_path)
	if not os.path.isfile(dll_test_path):
		raise SystemError('dll file was not moved from build directory')

	shutil.rmtree(build_fld)

if __name__ == '__main__':

	make_all()
