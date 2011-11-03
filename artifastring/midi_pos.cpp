#include "midi_pos.h"

// conversion utilities for midi, frequency, and position
#include <math.h>

const float SEMITONE = (float) pow(2, 1.0/12);

float midi2freq(float midi) {
    return (float) (440.0 * pow(2, (midi-69)/12.0));
}

float midi2pos(float relative_midi) {
    return (float) (1.0 - 1.0 / pow(SEMITONE, relative_midi));
}

float pos2midi(float position) {
    return (float) (12.0 * log(1.0 / (1.0-position)) / log(2.0));
}


