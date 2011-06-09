
artifastring_h = src/violin_constants.h \
	src/violin_body_impulse.h \
	src/violin_string.h src/violin_instrument.h
monowav_h = src/monowav.h

lib_LIBRARIES = libartifastring.a libmonowav.a
libartifastring_a_SOURCES = $(artifastring_h) \
	src/violin_string.cpp \
	src/violin_instrument.cpp
libmonowav_a_SOURCES = $(monowav_h) \
	src/monowav.cpp 
include_HEADERS = $(artifastring_h) $(monowav_h)

bin_PROGRAMS = actions2wav
actions2wav_SOURCES = $(libartifastring_a_SOURCES) \
	src/actions2wav.cpp


pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = artifastring.pc monowav.pc

#dist_noinst_SCRIPTS = autogen.sh

