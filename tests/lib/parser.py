# -*- coding: utf-8 -*-

"""

ZUGBRUECKE
Calling routines in Windows DLLs from Python scripts running on unixlike systems
https://github.com/pleiszenburg/zugbruecke

    tests/lib/parser.py: Extracting information from Python code without importing it

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

import ast

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# ROUTINES
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


def get_vars_from_source(src, *names, default=None):
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
        raise SyntaxError("unhandled type: %s (%s)" % (str(leaf), str(dir(leaf))))
