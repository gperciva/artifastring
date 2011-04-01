// simple.cpp
#include "violin_instrument.h"
#include "monowav.h"
int main () {
    // make objects
    MonoWav *wavfile = new MonoWav("output.wav");
    ViolinInstrument *violin = new ViolinInstrument();

    // get output buffer
    short *output = wavfile->request_fill(44100);

    // pluck the A string, in the middle of the string, with
    // moderately strong force
    violin->pluck(2, 0.5, 0.8);

    // wait 1 second
    violin->wait_samples(output, 44100);

    // automatically writes output file
    delete wavfile;
    delete violin;
}

