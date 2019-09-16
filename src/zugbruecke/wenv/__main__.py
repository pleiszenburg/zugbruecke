
import os
import sys

from .lib import env_class

env = env_class()

wine = env._wine_dict_[env.p['arch']]
cmd = env._cmd_dict_[ sys.argv[1] ]

os.execvpe(
	wine,
	(wine, cmd, *sys.argv[2:]),
	env._envvar_dict_,
	)
