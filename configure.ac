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
# required for swig, as part of Vivi if not Artifastring itself
CXXFLAGS="$CXXFLAGS -fPIC"

AC_MSG_CHECKING([build with debug information])
AC_ARG_ENABLE([debug],
    [AS_HELP_STRING([--enable-debug],
        [enable debug data generation (default=no)])],
    #[CXXFLAGS="$CXXFLAGS -g -fbounds-check -Wall -Werror -Wextra"],
    [CXXFLAGS="$CXXFLAGS -g -fbounds-check -Wall -Wextra"],
    [CXXFLAGS="$CXXFLAGS -O3 -funroll-loops"]
)



AC_CONFIG_MACRO_DIR([m4])
AX_PKG_SWIG()
AM_CONDITIONAL(HAS_SWIG, [test "x$SWIG" != 'x'])
AX_SWIG_ENABLE_CXX
AX_SWIG_PYTHON
AX_PYTHON_DEVEL
AM_PATH_PYTHON

AC_OUTPUT
