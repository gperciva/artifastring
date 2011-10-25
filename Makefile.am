### general setup
ACLOCAL_AMFLAGS = -I m4
if HAS_DEBUG
AM_CXXFLAGS = -fPIC -g -fbounds-check
MORE_WARNINGS_CXXFLAGS = -Wall -Werror -Wextra
else
AM_CXXFLAGS = -fPIC -O3 -march=native
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
	artifastring/violin_e_modes.h \
	artifastring/violin_a_modes.h \
	artifastring/violin_d_modes.h \
	artifastring/violin_g_modes.h \
	artifastring/cello_a_modes.h \
	artifastring/cello_d_modes.h \
	artifastring/cello_g_modes.h \
	artifastring/cello_c_modes.h \
	artifastring/violin_body_impulse.h \
	artifastring/violin_string.h \
	artifastring/violin_instrument.h
monowav_h = artifastring/monowav.h

lib_LIBRARIES = libartifastring.a libmonowav.a
libartifastring_a_SOURCES = $(artifastring_h) \
	artifastring/violin_string.cpp \
	artifastring/violin_instrument.cpp
libartifastring_a_CXXFLAGS = $(AM_CXXFLAGS) $(MORE_WARNINGS_CXXFLAGS)
artifastring_includedir=$(includedir)/artifastring/
libmonowav_a_SOURCES = $(monowav_h) \
	artifastring/monowav.cpp 
libmonowav_a_CXXFLAGS = $(AM_CXXFLAGS) $(MORE_WARNINGS_CXXFLAGS)
monowav_includedir=$(includedir)/artifastring/
nobase_include_HEADERS = $(artifastring_h) $(monowav_h)

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = artifastring.pc monowav.pc

ARTIFASTRING_INCLUDE = -I$(srcdir)/artifastring/

### binaries

bin_PROGRAMS = actions2wav
actions2wav_SOURCES = src/actions2wav.cpp
actions2wav_CXXFLAGS = $(AM_CXXFLAGS) $(ARTIFASTRING_INCLUDE) $(MORE_WARNINGS_CXXFLAGS)
actions2wav_LDADD = $(lib_LIBRARIES)

### swig
EXTRA_DIST += $(srcdir)/swig/monowav.i $(srcdir)/swig/violin_instrument.i

if HAS_SWIG
# unified definitions
SWIGCPP = $(PYTHON_CPPFLAGS) $(AX_SWIG_PYTHON_CPPFLAGS) $(ARTIFASTRING_INCLUDE)
SWIGLD = $(PYTHON_LDFLAGS) -module
swig/%_wrap.cxx swig/%.py: $(srcdir)/swig/%.i
	mkdir -p swig
	$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -o $@ $<

# per-file definitions
pyexec_LTLIBRARIES = _monowav.la _violin_instrument.la
nodist_python_PYTHON = swig/monowav.py swig/violin_instrument.py

nodist__monowav_la_SOURCES = swig/monowav_wrap.cxx \
	artifastring/monowav.cpp
_monowav_la_CPPFLAGS = $(SWIGCPP)
_monowav_la_LDFLAGS = $(SWIGLD)

nodist__violin_instrument_la_SOURCES = swig/violin_instrument_wrap.cxx \
	artifastring/violin_string.cpp \
	artifastring/violin_instrument.cpp
_violin_instrument_la_CPPFLAGS = $(SWIGCPP)
_violin_instrument_la_LDFLAGS = $(SWIGLD)

endif


### documentation
if HAS_DOXYGEN
# TODO: currently we always regenerate the docs when requested,
# but I figure this is hardly an important bug to fix.
docs:
	cd doc && $(DX_DOXYGEN) doxyfile
endif

if HAS_BLENDER
BLENDER_PYTHON_MODULES = blender/abstract_object.py \
	blender/artifastring-blender.py \
	blender/bow.py \
	blender/finger.py \
	blender/parse_actions.py \
	blender/pluck.py \
	blender/render_quality.py \
	blender/utils.py \
	blender/cameras.py \
	blender/violin.py

dist_pkgdata_DATA = blender/fast-violin.blend blender/violin-and-bow.blend
dist_pkgdata_DATA += $(BLENDER_PYTHON_MODULES)
# WTF?!  I started using autotools because I thought it would take
# care of this garbage for me.  :/
blender/actions2images.py: $(srcdir)/blender/actions2images.in.py
	mkdir -p blender/
	sed -e 's,$${datarootdir},${datarootdir},g' < $< > $@
bin_SCRIPTS = blender/actions2images.py \
	blender/artifastring-movie.py

endif
EXTRA_DIST += $(srcdir)/blender/actions2images.in.py
EXTRA_DIST += $(srcdir)/blender/artifastring-movie.py

