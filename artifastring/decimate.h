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
 */

#ifndef DECIMATE_H
#define DECIMATE_H

/*
 * This file has certain hard-coded values suitable for the
 * use in Artifastring, which may not be applicable for
 * other purposes.
 */

const int NZEROS = 4;
const int NPOLES = 4;

class Decimate {
public:
    Decimate(int factor_get);
    ~Decimate();
    void reset();

    void process(float *buffer_in, float *buffer_out, int num_samples_in);

private:
    int factor;

    float xv[NZEROS+1];
    float yv[NPOLES+1];
};

#endif



