ACLOCAL_AMFLAGS = -I m4

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
	$(libmonowav_a_SOURCES) \
	src/actions2wav.cpp


# TODO: so far I'm unable to make this section nice.  :(
pyexec_LTLIBRARIES = _monowav.la _violin_instrument.la
python_PYTHON = monowav.py violin_instrument.py

_monowav_la_SOURCES = monowav_wrap.cxx
_monowav_la_CPPFLAGS = -I$(PYTHON_INCLUDE)/ -I$(srcdir)/src/
_monowav_la_LDFLAGS = -module
monowav_wrap.cxx: $(srcdir)/swig/monowav.i
	$(SWIG) -c++ -python -I$(srcdir)/src/ -o $@ $<
_violin_instrument_la_SOURCES = violin_instrument_wrap.cxx
_violin_instrument_la_CPPFLAGS = -I$(PYTHON_INCLUDE)/ -I$(srcdir)/src/
_violin_instrument_la_LDFLAGS = -module
violin_instrument_wrap.cxx: $(srcdir)/swig/violin_instrument.i
	$(SWIG) -c++ -python -I$(srcdir)/src/ -o $@ $<




pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = artifastring.pc monowav.pc

#dist_noinst_SCRIPTS = autogen.sh

