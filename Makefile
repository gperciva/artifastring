CPP=g++
# FPIC required for swig
CPPFLAGS = -O3 \
	-FPIC \
	-funroll-loops

#CPPFLAGS = -g -fbounds-check -Wall


### actual user targets
all: actions2wav

doc:
	(cat Doxyfile ; echo "PROJECT_NUMBER=`cat VERSION`") | doxygen -

swig: _violin_instrument.so _monowav.so



### internal setup

VIOLIN_O = violin_instrument.o violin_string.o monowav.o

%.o: %.cpp violin_constants.h violin_body_impulse.h monowav.h
	$(CPP) -c $(CPPFLAGS) $< -o $@

actions2wav: actions2wav.cpp $(VIOLIN_O)
	g++ $(CPPFLAGS) $(VIOLIN_O) $< -o $@

# I feel dirty for using these special symbols.  Shouldn't have
# used a Makefile for this.  :(
%_wrap.o: %.i
	swig -c++ -python $<
	g++ $(CPPFLAGS) -c $*_wrap.cxx \
		-I/usr/include/python2.6

_violin_instrument.so: violin_instrument_wrap.o $(VIOLIN_O)
	g++ $(CPPFLAGS) -shared $< -o $@ \
		violin_string.o violin_instrument.o

_monowav.so: monowav_wrap.o $(VIOLIN_O)
	g++ $(CPPFLAGS) -shared $< -o $@ \
		monowav.o

# you can change 512 to 128 or 2048.
violin_body_impulse.h:
	echo "// This file was automatically generated" > $@
	echo "#ifndef IMPULSE_DATA_H" >> $@
	echo "#define IMPULSE_DATA" >> $@
	echo "const unsigned int PC_KERNEL_SIZE = 512;" >> $@
	echo "const double pc_kernel[] = {" >> $@
	sox impulses/impulse-512.wav -t dat - | \
		awk '$$1 != ";" { print "   ", $$2, ","}' >> $@
	echo "};" >> $@
	echo "#endif" >> $@

.PHONY: clean
clean:
	# main stuff
	rm -f actions2wav
	rm -f *.o
	rm -f *.pyc
	# swig stuff
	rm -f violin_instrument.py violin_instrument_wrap.cxx
	rm -f _*.so
	rm -f monowav.py monowav_wrap.cxx
	rm -rf html/




