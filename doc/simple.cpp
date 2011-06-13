// simple.cpp
#include "artifastring/violin_instrument.h"
#include "artifastring/monowav.h"
int main () {
    // make objects
    MonoWav *wavfile = new MonoWav("output.wav");
    ViolinInstrument *violin = new ViolinInstrument();

    // get output buffer
    short *output = wavfile->request_fill(44100);

    // pluck the A string, near the middle of the string,
    // with moderately strong force
    violin->pluck(2, 0.45, 0.8);

    // wait 1 second
    violin->wait_samples(output, 44100);

    // automatically writes output file
    delete wavfile;
    delete violin;
}

