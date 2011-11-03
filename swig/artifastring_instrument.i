%module artifastring_instrument
%{
#define SWIG_FILE_WITH_INIT
#include "artifastring_instrument.h"
%}

%include "artifastring_defines.h"

/*
  used to set modal decay values in constant-randomization script
*/
%include "carrays.i"
%array_functions(float, floatArray);
%array_class(short, shortArray);

/*
  interface with numpy
*/
%include "numpy.i"

%init %{
import_array();
%}

%apply (float* INPLACE_ARRAY1, int DIM1) {(float *buffer, int num_samples)};
%apply (short* INPLACE_ARRAY1, int DIM1) {(short *buffer, int num_samples)};
%apply (short* INPLACE_ARRAY1, int DIM1) {
    (short *buffer, int num_samples), (short *forces, int num_samples2)};
%include "artifastring_instrument.h"

%inline %{
    int wait_samples_c(ArtifastringInstrument *inst, short *buffer_py, int n) {
        return inst->wait_samples(buffer_py, n);
    }
%}

