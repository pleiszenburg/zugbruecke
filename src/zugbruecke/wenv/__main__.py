
import os

from .lib import env_class

env = env_class()

os.execvpe(
	'wine',
	('wine', env._path_dict_['interpreter'],),
	env._envvar_dict_,
	)
