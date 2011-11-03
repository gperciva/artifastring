%module monowav
%{
#include "monowav.h"
%}

%include "monowav.h"

%include "carrays.i"
%array_class(short, shortArray);

