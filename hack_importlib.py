
PATH_OLD = '/tmp/wenv-75360f3b/Lib/importlib/_bootstrap_external.pyc'
PATH_NEW = '/tmp/wenv-75360f3b/Lib/importlib/_bootstrap_external.py'
# PATH_OLD = '/tmp/wenv-03329cbd/Lib/importlib/_bootstrap_external.pyc'
# PATH_NEW = '/tmp/wenv-03329cbd/Lib/importlib/_bootstrap_external.py'
URL = 'http://raw.githubusercontent.com/python/cpython/v3.7.4/Lib/importlib/_bootstrap_external.py'

OLD = '            contents = _os.listdir(path or _os.getcwd())'
NEW = """
            def _print(nr, data):
                text_out = str(data).encode('utf-8')
                fd = _os.open('/tmp/wenv-75360f3b/log_%d.txt' % nr, _os.O_CREAT | _os.O_WRONLY)
                _os.writev(fd, text_out)
                _os.close(fd)
            _print(1, path)
            _print(2, type(path))
            _print(3, _os.getcwd())
            _print(4, path or _os.getcwd())
            _print(5, _os.listdir(path or _os.getcwd()))
            contents = _os.listdir(path or _os.getcwd())
"""

import os
import urllib.request
import sys

def _print(text):
    sys.stderr.write(text + '\n')
    sys.stderr.flush()

def main():

    if os.path.exists(PATH_OLD):
        os.unlink(PATH_OLD)

    urllib.request.urlretrieve(URL, PATH_NEW)

    with open(PATH_NEW, 'r') as f:
        data = f.read()

    data = data.replace(OLD, NEW)

    with open(PATH_NEW, 'w') as f:
        f.write(data)

if __name__ == '__main__':

    main()
