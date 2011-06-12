#AC_INIT([Artifastring], [1.6], [graham@percival-music.ca], [artifastring], [http://percival-music.ca/artifastring/])
AC_INIT([Artifastring], [esyscmd([head -n 1 VERSION | tr -d '\n'])], [graham@percival-music.ca], [artifastring], [http://percival-music.ca/artifastring/])
# override flags that AC_INIT sets up, but keeping any flags the
# user sets
: ${CXXFLAGS=""}

AC_PREREQ([2.59])
AM_INIT_AUTOMAKE([1.10 no-define foreign -Wall -Werror])
AC_CONFIG_HEADERS([config.h])
AC_PROG_CXX
AC_PROG_LIBTOOL
AC_CONFIG_FILES([Makefile artifastring.pc monowav.pc])
# required for swig
CXXFLAGS="$CXXFLAGS -fPIC"


AC_CONFIG_MACRO_DIR([m4])
AM_PATH_PYTHON
#AC_PROG_SWIG
#SWIG_ENABLE_CXX
#SWIG_PYTHON
AX_PKG_SWIG(, [], [])
#AC_MSG_ERROR([SWIG is recommended; python modules will not be built otherwise])])


AC_ARG_VAR([PYTHON_INCLUDE], [Include flags for python, bypassing
python-config])
AC_ARG_VAR([PYTHON_CONFIG], [Path to python-config])
AS_IF([test -z "$PYTHON_INCLUDE"], [
  AS_IF([test -z "$PYTHON_CONFIG"], [
    AC_PATH_PROGS([PYTHON_CONFIG],
                  [python$PYTHON_VERSION-config python-config],
                  [no],
                  [`dirname $PYTHON`])
    AS_IF([test "$PYTHON_CONFIG" = no], [AC_MSG_ERROR([cannot find
python-config for $PYTHON.])])
  ])
  AC_MSG_CHECKING([python include flags])
  PYTHON_INCLUDE=`$PYTHON_CONFIG --includes`
  AC_MSG_RESULT([$PYTHON_INCLUDE])
])


AC_OUTPUT
