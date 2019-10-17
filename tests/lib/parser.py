
import ast

def get_vars_from_source(src, *names, default = None):
	tree = ast.parse(src)
	out_dict = {name: default for name in names}
	for item in tree.body:
		if not isinstance(item, ast.Assign):
			continue
		for target in item.targets:
			if target.id not in names:
				continue
			out_dict[target.id] = _parse_tree(item.value)
	return out_dict

def _parse_tree(leaf):
	if isinstance(leaf, ast.Str) or isinstance(leaf, ast.Bytes):
		return leaf.s
	elif isinstance(leaf, ast.Num):
		return leaf.n
	elif isinstance(leaf, ast.NameConstant):
		return leaf.value
	elif isinstance(leaf, ast.Dict):
		return {
			_parse_tree(leaf_key): _parse_tree(leaf_value)
			for leaf_key, leaf_value in zip(leaf.keys, leaf.values)
			}
	elif isinstance(leaf, ast.List):
		return [_parse_tree(leaf_item) for leaf_item in leaf.elts]
	elif isinstance(leaf, ast.Tuple):
		return tuple([_parse_tree(leaf_item) for leaf_item in leaf.elts])
	elif isinstance(leaf, ast.Set):
		return {_parse_tree(leaf_item) for leaf_item in leaf.elts}
	else:
		raise SyntaxError('unhandled type: %s (%s)' % (str(leaf), str(dir(leaf))))
