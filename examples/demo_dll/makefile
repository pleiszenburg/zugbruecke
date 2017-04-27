CC      = i686-w64-mingw32-gcc
CFLAGS  = -Wall -Wl,-add-stdcall-alias -shared
LDFLAGS = 

DEMODLL = demo_dll
DEMODLL_C = $(DEMODLL).c
DEMODLL_LDFLAGS = 

all: $(DEMODLL)

$(DEMODLL): $(DEMODLL_C)
	$(CC) $(DEMODLL_C) $(CFLAGS) -o ../$(DEMODLL).dll $(LDFLAGS) $(DEMODLL_LDFLAGS)

clean:
	rm ../$(DEMODLL).dll
