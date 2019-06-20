AC_INIT([Artifastring], [2.4], [graham@percival-music.ca], [artifastring],
  [http://percival-music.ca/artifastring/])
# override flags from AC_INIT, but keeps any flags the user sets
: ${CXXFLAGS=""}

# directories
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_AUX_DIR([libtool-aux])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_FILES([Makefile artifastring.pc monowav.pc doc/doxyfile])

AC_PREREQ([2.59])
AM_INIT_AUTOMAKE([1.10 subdir-objects no-define foreign -Wall -Werror])
AM_PROG_AR


### libraries
AC_PROG_CXX
AC_PROG_LIBTOOL
AC_HEADER_STDC

AC_LANG([C++])

AC_CHECK_LIB(stdc++, main,, AC_MSG_ERROR(requires libstdc++))
AC_CHECK_LIB(m, main,, AC_MSG_ERROR(requires libm (math)))
AC_CHECK_LIB(fftw3f, main,, AC_MSG_ERROR(requires libfftw3))

AC_ARG_ENABLE([debug],
  [AS_HELP_STRING(--enable-debug,[Compile with debug support])],
  [],
  [enable_debug="no"])
AM_CONDITIONAL([HAS_DEBUG], [test "x$enable_debug" != xno])

AC_ARG_WITH([eigen],
  [AS_HELP_STRING(--with-eigen=<path>,
    [Specify path to eigen headers. Default is /usr/include/eigen3])],
  [echo eigen arg $with_eigen],
  [echo with-eigen not used. ; with_eigen=default])
  
EIGEN3_CFLAGS=/usr/include/eigen3
AS_IF([test "x${with_eigen}" = xno], [AC_MSG_WARN(m4_normalize(
        [Artifastring requires Eigen. The --with-eigen flag allows you to
         specify the path to the Eigen headers, not to despense with them.
         Configuration will continue, checking the default location for
         the Eigen headers, namely ${EIGEN3_CFLAGS}]))],
      [test "x${with_eigen}" = xyes], [AC_MSG_WARN(m4_normalize(
        [Using --with-eigen without an argument is just the default behaviour.
         This option only makes sense when you specify the Eigen include path]))],
      [test "x${with_eigen}" = xdefault], [],
      [EIGEN3_CFLAGS=${with_eigen}])

      echo $with_eigen $EIGEN3_CFLAGS
      
AC_CHECK_HEADER(${EIGEN3_CFLAGS}/Eigen/Core,
  [AC_SUBST([eigen3_cflags], ["-I${EIGEN3_CFLAGS}"])],
  [AC_MSG_ERROR([I looked for Eigen/Core in ${EIGEN3_CFLAGS} and failed to find it])],
  [AC_INCLUDES_DEFAULT])

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


AC_CANONICAL_HOST
case "$host_os" in 
  darwin* )
    DARWIN=yes
    ;;
  *)
    DARWIN=no
    ;;
esac
AM_CONDITIONAL([IS_DARWIN], [test "x$DARWIN" != xno])


AC_OUTPUT
