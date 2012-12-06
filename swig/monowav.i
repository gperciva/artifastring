%module monowav
%{
#include "monowav.h"
%}

%include "monowav.h"

%include "carrays.i"
%array_class(short, shortArray);

%inline %{
  void buffer_set(short* buf, int i, short x) {
    buf[i] = x;
  }
%}


