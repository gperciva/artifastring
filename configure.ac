AC_INIT([Artifastring], [2.2], [graham@percival-music.ca], [artifastring],
  [http://percival-music.ca/artifastring/])
# override flags from AC_INIT, but keeps any flags the user sets
: ${CXXFLAGS=""}

# directories
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_AUX_DIR([libtool-aux])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile artifastring.pc monowav.pc doc/doxyfile])

AC_PREREQ([2.59])
AM_INIT_AUTOMAKE([1.10 no-define foreign -Wall -Werror])
AM_PROG_AR


### libraries
AC_PROG_CXX
AC_PROG_LIBTOOL
AC_HEADER_STDC

#AC_LANG([C++])

AC_CHECK_LIB(stdc++, main,, AC_MSG_ERROR(requires libstc++))
AC_CHECK_LIB(m, main,, AC_MSG_ERROR(requires libm (math)))
AC_CHECK_LIB(fftw3f, main,, AC_MSG_ERROR(requires libfftw3))

AC_ARG_ENABLE([debug],
  [AS_HELP_STRING(--enable-debug,[Compile with debug support])],
  [],
  [enable_debug="no"])
AM_CONDITIONAL([HAS_DEBUG], [test "x$enable_debug" != xno])


### swig stuff
AC_ARG_WITH(swig,
  [AS_HELP_STRING(--with-swig,[Python bindings with swig])],
  [],
  [with_swig="no"])
AM_CONDITIONAL([HAS_SWIG], [test "x$with_swig" != xno])
AS_IF([test "x$with_swig" != xno],
  [
  AM_PATH_PYTHON
  AX_PYTHON_DEVEL
  AX_PKG_SWIG()
  AX_SWIG_ENABLE_CXX
  AX_SWIG_PYTHON
  ], [])


### play nice with other fftw users
AC_ARG_ENABLE([fftw-cleanup-elsewhere],
  [AS_HELP_STRING(--enable-fftw-cleanup-elsewhere,
    [Other code will call fftw_cleanup()])],
  [AC_DEFINE(FFTW_CLEANUP_ELSEWHERE, 1,
    [Other code will call fftw_cleanup((])],
  [AC_DEFINE(FFTW_CLEANUP_ELSEWHERE, 0,
    [Other code will call fftw_cleanup((])]
  )

### doc stuff
DX_INIT_DOXYGEN(artifastring, doc/doxygen, [out-www/])
AM_CONDITIONAL([HAS_DOXYGEN], [test "x$DX_DOXYGEN" != 'x'])


### blender stuff
AC_ARG_ENABLE([blender],
  [AS_HELP_STRING(--enable-blender,[Install blender animation support.])],
  [],
  [enable_blender="no"])
AM_CONDITIONAL([HAS_BLENDER], [test "x$enable_blender" != xno])
AS_IF([test "x$enable_blender" != xno],
  [
  AC_CHECK_PROG(BLENDER, blender, [yes],
    [Blender 2.5+ is required to generate animations])
  ], [])


AC_OUTPUT
