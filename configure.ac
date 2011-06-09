#AC_INIT([Artifastring], [1.6], [graham@percival-music.ca], [artifastring], [http://percival-music.ca/artifastring/])
AC_INIT([Artifastring], [esyscmd([head -n 1 VERSION | tr -d '\n'])], [graham@percival-music.ca], [artifastring], [http://percival-music.ca/artifastring/])
AC_PREREQ([2.59])
AM_INIT_AUTOMAKE([1.10 no-define foreign -Wall -Werror])
AC_CONFIG_HEADERS([config.h])
AC_PROG_CXX
AC_PROG_RANLIB
AC_CONFIG_FILES([Makefile artifastring.pc monowav.pc])
AC_OUTPUT
