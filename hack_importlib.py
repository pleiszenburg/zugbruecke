
PATH_OLD = '/tmp/wenv-75360f3b/Lib/importlib/_bootstrap_external.pyc'
PATH_NEW = '/tmp/wenv-75360f3b/Lib/importlib/_bootstrap_external.py'
URL = 'http://raw.githubusercontent.com/python/cpython/v3.7.4/Lib/importlib/_bootstrap_external.py'

OLD = '            contents = _os.listdir(path or _os.getcwd())'
NEW = """
            print('XX 1 XX', path)
            print('XX 2 XX', type(path))
            print('XX 3 XX', _os.getcwd())
            print('XX 4 XX', path or _os.getcwd())
            print('XX 5 XX', _os.listdir(path or _os.getcwd()))
            contents = _os.listdir(path or _os.getcwd())
"""

import os
import urllib.request

def main():

    os.unlink(PATH_OLD)
    urllib.request.urlretrieve(URL, PATH_NEW)

    with open(PATH_NEW, 'r') as f:
        data = f.read()

    data = data.replace(OLD, NEW)

    with open(PATH_NEW, 'w') as f:
        f.write(data)

if __name__ == '__main__':

    main()
