### general setup
ACLOCAL_AMFLAGS = -I m4
if HAS_DEBUG
AM_CXXFLAGS = -Iotherlibs/ -I../otherlibs/ -fPIC -g -fbounds-check
MORE_WARNINGS_CXXFLAGS = -Wall -Werror -Wextra
else
if IS_DARWIN
AM_CXXFLAGS = -Iotherlibs/ -I../otherlibs/ -fPIC -O3 -mtune=native -DNDEBUG
else
AM_CXXFLAGS = -Iotherlibs/ -I../otherlibs/ -fPIC -O3 -march=native -DNDEBUG
endif
MORE_WARNINGS_CXXFLAGS =
endif


EXTRA_DIST = autogen.sh otherlibs \
	research interactive actions \
	doc/main_page.doxy doc/simple.cpp \
	make-release.sh \
	artifastring-logo.svg

### this handy hook comes from:
### https://github.com/gfxmonk/gnome-shell/blob/d62b4cf130abca975f16be987c51279037020a50/Makefile.am
#distcheck-hook:
#	@echo "Checking disted files against files in git"
#	@failed=false; \
#	#exclude=`(for p in $(DIST_EXCLUDE) ; do echo --exclude=$$p ; done)`;
#	for f in `cd $(srcdir) && git ls-files --ignored --exclude-standard` ; do \
#		if ! test -e $(distdir)/$$f ; then \
#			echo File missing from distribution: $$f ; \
#			failed=true ; \
#		fi \
#	done ; \
#	if $$failed ; then \
#		exit 1 ; \
#	fi ;


clean-local:
	rm -rf doc/html/
	rm -f monowav.py artifastring_instrument.py
	rm -f monowav_wrap.cxx artifastring_instrument_wrap.cxx

# this is a hacky way to only remove doc/ if we're
# in a build dir, but not if we're in the main source dir
distclean-local:
	[ -e doc/doxyfile.in ] || rmdir doc/


### libraries
artifastring_h = artifastring/artifastring_constants.h \
	artifastring/artifastring_defines.h \
	artifastring/constants/strings_violin.h \
	artifastring/constants/strings_viola.h \
	artifastring/constants/strings_cello.h \
	artifastring/constants/body_violin_1.h \
	artifastring/constants/body_viola_1.h \
	artifastring/constants/body_cello_1.h \
	artifastring/constants/lowpass_1.h \
	artifastring/constants/lowpass_2.h \
	artifastring/constants/lowpass_3.h \
	artifastring/constants/lowpass_4.h \
	artifastring/constants/haptic_response_1.h \
	artifastring/constants/haptic_response_2.h \
	artifastring/constants/haptic_response_3.h \
	artifastring/constants/haptic_response_4.h \
	artifastring/actions_file.h \
	artifastring/midi_pos.h \
	artifastring/decimate.h \
	artifastring/fft_convolution.h \
	artifastring/artifastring_string.h \
	artifastring/artifastring_instrument.h
monowav_h = artifastring/monowav.h

lib_LIBRARIES = libartifastring.a libmonowav.a
libartifastring_a_SOURCES = $(artifastring_h) \
	artifastring/actions_file.cpp \
	artifastring/midi_pos.cpp \
	artifastring/decimate.cpp \
	artifastring/fft_convolution.cpp \
	artifastring/artifastring_string.cpp \
	artifastring/artifastring_instrument.cpp
libartifastring_a_CXXFLAGS = $(AM_CXXFLAGS) \
	$(MORE_WARNINGS_CXXFLAGS) \
	$(EIGEN3_CFLAGS)
artifastring_includedir=$(includedir)/artifastring/
libmonowav_a_SOURCES = $(monowav_h) \
	artifastring/monowav.cpp 
libmonowav_a_CXXFLAGS = $(AM_CXXFLAGS) $(MORE_WARNINGS_CXXFLAGS) \
	$(EIGEN3_CFLAGS)
monowav_includedir=$(includedir)/artifastring/
nobase_include_HEADERS = $(artifastring_h) $(monowav_h)

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = artifastring.pc monowav.pc

ARTIFASTRING_INCLUDE = -I$(srcdir)/artifastring/

### binaries

bin_PROGRAMS = actions2wav
actions2wav_SOURCES = src/actions2wav.cpp
actions2wav_CXXFLAGS = $(AM_CXXFLAGS) $(ARTIFASTRING_INCLUDE) \
	$(MORE_WARNINGS_CXXFLAGS) \
	$(EIGEN3_CFLAGS)
actions2wav_LDADD = $(lib_LIBRARIES) \
	$(EIGEN3_LIBS)


### setup for += later
bin_SCRIPTS =


### swig
EXTRA_DIST += \
	$(srcdir)/swig/monowav.i \
	$(srcdir)/swig/artifastring_instrument.i \
	$(srcdir)/swig/actions_file.i \
	$(srcdir)/swig/midi_pos.i \
	$(srcdir)/swig/numpy.i \
	$(srcdir)/swig/pyfragments.swg

if HAS_SWIG
# unified definitions
SWIGCPP = $(PYTHON_CPPFLAGS) $(AX_SWIG_PYTHON_CPPFLAGS) $(ARTIFASTRING_INCLUDE)
SWIGLD = $(PYTHON_LDFLAGS) -module
swig/%_wrap.cxx swig/%.py: $(srcdir)/swig/%.i
	mkdir -p swig
	$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -builtin -o $@ $<
#$(SWIG) $(AX_SWIG_PYTHON_OPT) $(ARTIFASTRING_INCLUDE) -o $@ $<

# per-file definitions
pyexec_LTLIBRARIES = _monowav.la _artifastring_instrument.la \
	_actions_file.la _midi_pos.la
python_PYTHON = interactive/artifastring_interactive.py \
	interactive/artifastring_osc.py \
	interactive/artifastring_process.py \
	interactive/quality_judgements.py \
	interactive/tuning_pitch.py \
	interactive/enum.py
nodist_python_PYTHON = swig/monowav.py swig/artifastring_instrument.py \
	swig/actions_file.py swig/midi_pos.py
bin_SCRIPTS += interactive/artifastring_play_osc.py \
	interactive/artifastring_play_interactive.py

nodist__monowav_la_SOURCES = swig/monowav_wrap.cxx \
	artifastring/monowav.cpp
_monowav_la_CPPFLAGS = $(SWIGCPP) $(EIGEN3_CFLAGS)
_monowav_la_LDFLAGS = $(SWIGLD) $(EIGEN3_LIBS)

nodist__artifastring_instrument_la_SOURCES = swig/artifastring_instrument_wrap.cxx \
	artifastring/artifastring_string.cpp \
	artifastring/fft_convolution.cpp \
	artifastring/artifastring_instrument.cpp
_artifastring_instrument_la_CPPFLAGS = $(SWIGCPP) $(EIGEN3_CFLAGS)
_artifastring_instrument_la_LDFLAGS = $(SWIGLD) $(EIGEN3_LIBS)

nodist__actions_file_la_SOURCES = swig/actions_file_wrap.cxx \
	artifastring/actions_file.cpp
_actions_file_la_CPPFLAGS = $(SWIGCPP) $(EIGEN3_CFLAGS)
_actions_file_la_LDFLAGS = $(SWIGLD) $(EIGEN3_LIBS)

nodist__midi_pos_la_SOURCES = swig/midi_pos_wrap.cxx \
	artifastring/midi_pos.cpp
_midi_pos_la_CPPFLAGS = $(SWIGCPP) $(EIGEN3_CFLAGS)
_midi_pos_la_LDFLAGS = $(SWIGLD) $(EIGEN3_LIBS)


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
	blender/artifastring_blender.py \
	blender/bow.py \
	blender/finger.py \
	blender/parse_actions.py \
	blender/pluck.py \
	blender/render_quality.py \
	blender/utils.py \
	blender/cameras.py \
	blender/violin.py

dist_pkgdata_DATA = blender/fast-violin.blend blender/violin-and-bow.blend \
	blender/MAKING-A-MODEL.txt blender/README
dist_pkgdata_DATA += $(BLENDER_PYTHON_MODULES)
# WTF?!  I started using autotools because I thought it would take
# care of this garbage for me.  :/
blender/actions2images.py: $(srcdir)/blender/actions2images.in.py
	mkdir -p blender/
	sed -e 's,$${datarootdir},${datarootdir},g' < $< > $@
bin_SCRIPTS += blender/actions2images.py \
	blender/artifastring_movie.py

endif
EXTRA_DIST += $(srcdir)/blender/actions2images.in.py
EXTRA_DIST += $(srcdir)/blender/artifastring_movie.py



