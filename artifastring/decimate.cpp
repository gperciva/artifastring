/*
 * Copyright 2010--2011 Graham Percival
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

#include "decimate.h"

#include <assert.h>

#include <stdio.h>

Decimate::Decimate(int factor_get)
{
    factor = factor_get;
    reset();
}

Decimate::~Decimate()
{
}

void Decimate::reset()
{
    for (int i=0; i<NZEROS; i++) {
        yv[i] = 0;
    }
    for (int i=0; i<NPOLES; i++) {
        xv[i] = 0;
    }
}

void Decimate::process(float *buffer_in, float *buffer_out, int num_samples)
{
    assert(num_samples % factor == 0);
    // FIXME: implement phase FIR
    // do filter first
    for (int i=0; i<num_samples; i++) {
        xv[0] = xv[1];
        xv[1] = xv[2];
        xv[2] = xv[3];
        xv[3] = xv[4];
        yv[0] = yv[1];
        yv[1] = yv[2];
        yv[2] = yv[3];
        yv[3] = yv[4];
        xv[4] = buffer_in[i];
        yv[4] = (xv[0] + xv[4]) + 4 * (xv[1] + xv[3]) + 6 * xv[2]
                + ( -0.0745545378 * yv[0]) + (  0.4749425707 * yv[1])
                + ( -1.2568028304 * yv[2]) + (  1.5518168271 * yv[3]);
        buffer_in[i] = yv[4];
    }
    // downsample
    for (int i=0; i<num_samples/factor; i++) {
        buffer_out[i] = buffer_in[i*factor];
        //printf("\n");
    }
}


