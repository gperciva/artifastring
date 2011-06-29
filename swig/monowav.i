%module monowav
%{
#include "monowav.h"
%}

%include "monowav.h"

/*
  useful for quick experiments with RMS of output
*/
%include "carrays.i"
%array_class(short, shortArray);

