/*
 * Copyright 2010--2013 Graham Percival
 * This file is part of Artifastring.
 *
 * Artifastring is free software: you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 *
 * Artifastring is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public
 * License along with Artifastring.  If not, see
 * <http://www.gnu.org/licenses/>.
 *
 */

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


