### general setup
ACLOCAL_AMFLAGS = -I m4
if HAS_DEBUG
AM_CXXFLAGS = -fPIC -g -fbounds-check
MORE_WARNINGS_CXXFLAGS = -Wall -Werror -Wextra
else
AM_CXXFLAGS = -fPIC -O3 -funroll-loops
MORE_WARNINGS_CXXFLAGS =
endif

EXTRA_DIST = autogen.sh

clean-local:
	rm -rf doc/html/
	rm -f monowav.py violin_instrument.py
	rm -f monowav_wrap.cxx violin_instrument_wrap.cxx

# this is a hacky way to only remove doc/ if we're
# in a build dir, but not if we're in the main source dir
distclean-local:
	[ -e doc/doxyfile.in ] || rmdir doc/


### libraries
artifastring_h = artifastring/violin_constants.h \
	artifastring/violin_body_impulse.h \
	artifastring/violin_string.h \
	artifastring/violin_instrument.h
monowav_h = artifastring/monowav.h

lib_LIBRARIES = libartifastring.a libmonowav.a
libartifastring_a_SOURCES = $(artifastring_h) \
	artifastring/violin_string.cpp \
	artifastring/violin_instrument.cpp
libartifastring_a_CXXFLAGS = $(MORE_WARNINGS_CXXFLAGS)
artifastring_includedir=$(includedir)/artifastring/
libmonowav_a_SOURCES = $(monowav_h) \
	artifastring/monowav.cpp 
libmonowav_a_CXXFLAGS = $(MORE_WARNINGS_CXXFLAGS)
monowav_includedir=$(includedir)/artifastring/
nobase_include_HEADERS = $(artifastring_h) $(monowav_h)

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = artifastring.pc monowav.pc

ARTIFASTRING_INCLUDE = -I$(srcdir)/artifastring/

### binaries

bin_PROGRAMS = actions2wav
actions2wav_SOURCES = src/actions2wav.cpp
actions2wav_CXXFLAGS = $(ARTIFASTRING_INCLUDE) $(MORE_WARNINGS_CXXFLAGS)
actions2wav_LDADD = $(lib_LIBRARIES)

### swig
# TODO: so far I'm unable to make this section nice.  :(
if HAS_SWIG
EXTRA_DIST += $(srcdir)/swig/monowav.i $(srcdir)/swig/violin_instrument.i

pyexec_LTLIBRARIES = _monowav.la _violin_instrument.la
python_PYTHON = monowav.py violin_instrument.py

_monowav_la_SOURCES = monowav_wrap.cxx
_monowav_la_CPPFLAGS = $(PYTHON_CPPFLAGS) $(AX_SWIG_PYTHON_CPPFLAGS) \
	$(ARTIFASTRING_INCLUDE)
_monowav_la_LDFLAGS = $(PYTHON_LDFLAGS) -module -lmonowav
monowav_wrap.cxx: $(srcdir)/swig/monowav.i
	$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -o $@ $<
monowav.py: $(srcdir)/swig/monowav.i
	$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -o $@ $<
_violin_instrument_la_SOURCES = violin_instrument_wrap.cxx
_violin_instrument_la_CPPFLAGS = $(PYTHON_CPPFLAGS) $(AX_SWIG_PYTHON_CPPFLAGS) \
	$(ARTIFASTRING_INCLUDE)
_violin_instrument_la_LDFLAGS = $(PYTHON_LDFLAGS) -module -lartifastring
violin_instrument_wrap.cxx: $(srcdir)/swig/violin_instrument.i
	$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -o $@ $<
violin_instrument.py: $(srcdir)/swig/violin_instrument.i
	$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -o $@ $<
endif


### documentation
if HAS_DOXYGEN
# TODO: currently we always regenerate the docs when requested,
# but I figure this is hardly an important bug to fix.
docs:
	cd doc && $(DX_DOXYGEN) doxyfile
endif


