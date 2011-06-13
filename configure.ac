AC_INIT([Artifastring], [1.6], [graham@percival-music.ca], [artifastring], [http://percival-music.ca/artifastring/])
# override flags from AC_INIT, but keeps any flags the user sets
: ${CXXFLAGS=""}

AC_PREREQ([2.59])
AM_INIT_AUTOMAKE([1.10 no-define foreign -Wall -Werror])
AC_CONFIG_MACRO_DIR([m4])
AC_CONFIG_HEADERS([config.h])

### libraries
AC_PROG_CXX
AC_PROG_LIBTOOL
AC_CONFIG_FILES([Makefile artifastring.pc monowav.pc])

AC_ARG_ENABLE([debug],
  [  --enable-debug    Turn on debugging],
  [case "${enableval}" in
    yes) debug=true ;;
    no)  debug=false ;;
    *) AC_MSG_ERROR([bad value ${enableval} for --enable-debug]) ;; esac],
  [debug=false])
AM_CONDITIONAL([HAS_DEBUG], [test x$debug = xtrue])


### swig stuff
AX_PKG_SWIG()
AM_CONDITIONAL(HAS_SWIG, [test "x$SWIG" != 'x'])
AX_SWIG_ENABLE_CXX
AX_SWIG_PYTHON
AX_PYTHON_DEVEL
AM_PATH_PYTHON

### doc stuff
DX_INIT_DOXYGEN(artifastring, doc, [out-www/])

AC_OUTPUT
