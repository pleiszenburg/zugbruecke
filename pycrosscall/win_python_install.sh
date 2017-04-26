
arch=win32
version=3.5.3

pyarchive=python-$version-embed-$arch.zip
pydir=$arch-python$version

wget https://www.python.org/ftp/python/$version/$pyarchive
unzip $pyarchive -d $pydir
rm $pyarchive
