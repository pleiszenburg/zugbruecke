
arch=win32
version=3.5.3

pydir=../zugbruecke/$arch-python$version

export WINEARCH="$arch"
export WINEPREFIX="$(pwd)/../zugbruecke/$arch-wine"
cd $pydir

wine python.exe
