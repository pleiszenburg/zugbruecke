
arch=win32
version=3.5.3

pydir=$arch-python$version

export WINEARCH="$arch"
export WINEPREFIX="$(pwd)/$arch-wine"
cd $arch-python$version
wine python.exe
