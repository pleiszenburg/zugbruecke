
import os

from .lib import env_class

env = env_class()

import sys; print(sys.argv)

os.execvpe(
	'wine',
	('wine', env._path_dict_['interpreter'], *sys.argv[1:]),
	env._envvar_dict_,
	)
