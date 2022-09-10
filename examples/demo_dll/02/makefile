# ZUGBRUECKE
# Calling routines in Windows DLLs from Python scripts running on unixlike systems
# https://github.com/pleiszenburg/zugbruecke
#
#	demo_dll/02/makefile: GNU makefile for building demo DLL with mingw
#
#	Required to run on platform / side: [UNIX]
#
# 	Copyright (C) 2017-2022 Sebastian M. Ernst <ernst@pleiszenburg.de>
#
# <LICENSE_BLOCK>
# The contents of this file are subject to the GNU Lesser General Public License
# Version 2.1 ("LGPL" or "License"). You may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# https://www.gnu.org/licenses/old-licenses/lgpl-2.1.txt
# https://github.com/pleiszenburg/zugbruecke/blob/master/LICENSE
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License for the
# specific language governing rights and limitations under the License.
# </LICENSE_BLOCK>


CC      = i686-w64-mingw32-gcc
# CFLAGS  = -Wall -Wl,-add-stdcall-alias -shared -std=c99
CFLAGS  = -Wall -Wl,--subsystem,windows -shared -std=c99
LDFLAGS = -lm

DEMODLL = demo_dll
DEMODLL_C = $(DEMODLL).c
DEMODLL_LDFLAGS =

all: $(DEMODLL)

$(DEMODLL): $(DEMODLL_C)
	$(CC) $(DEMODLL_C) $(CFLAGS) -o $(DEMODLL).dll $(LDFLAGS) $(DEMODLL_LDFLAGS)

# install:
# 	ln -s ../$(DEMODLL)/$(DEMODLL).dll ../examples/$(DEMODLL).dll
# 	ln -s ../$(DEMODLL)/$(DEMODLL).dll ../tests_old/$(DEMODLL).dll

clean:
	-rm $(DEMODLL).dll
	# -rm ../examples/$(DEMODLL).dll
	# -rm ../tests_old/$(DEMODLL).dll
