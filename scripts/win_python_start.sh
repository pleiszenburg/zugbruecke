
arch=win32
version=3.5.3

pydir=../pycrosscall/$arch-python$version

export WINEARCH="$arch"
export WINEPREFIX="$(pwd)/../pycrosscall/$arch-wine"
cd $pydir

wine python.exe
