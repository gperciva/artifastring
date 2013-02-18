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

#ifndef ARTIFASTRING_DEFINES_H
#define ARTIFASTRING_DEFINES_H

/** @file
 *
 *
 * artifastring_defines.h is included in the swig .py files,
 * whereas artifastring_constants.h is not.
 */

//#define EIGEN_DONT_VECTORIZE

//#define RESEARCH
//#define HIGH_FREQUENCY_NO_DOWNSAMPLING

//#define DEBUG_WITH_WHITE_NOISE


//#define BODY_ONLY_LOWPASS 0.1


const int MAX_MODAL_DECAY_MODES = 128;

#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
const int ARTIFASTRING_INSTRUMENT_SAMPLE_RATE = 22050*4;
//
const int HAPTIC_DOWNSAMPLE_FACTOR = 1;
#else
const int ARTIFASTRING_INSTRUMENT_SAMPLE_RATE = 44100;
const int HAPTIC_DOWNSAMPLE_FACTOR = 2;
#endif

//const int ARTIFASTRING_INSTRUMENT_SAMPLE_RATE = 66150;
//const int ARTIFASTRING_INSTRUMENT_SAMPLE_RATE = 44100;
const int HAPTIC_SAMPLE_RATE = ARTIFASTRING_INSTRUMENT_SAMPLE_RATE / HAPTIC_DOWNSAMPLE_FACTOR;
//const int HAPTIC_DOWNSAMPLE_FACTOR = 8;
//const int HAPTIC_SAMPLE_RATE = ARTIFASTRING_SAMPLE_RATE / HAPTIC_DOWNSAMPLE_FACTOR;

//const int NORMAL_BUFFER_SIZE = 1024;
const int NORMAL_BUFFER_SIZE = 512;

/**
 * \enum InstrumentType
 *
 * Enumeration type to select instrument family.  After selecting
 * the instrument family, the specific instrument within that
 * family can be selected.  Each instrument family has a different
 * number of available instruments.  Instrument numbers begin at
 * 0.
 */
enum InstrumentType {
    /// 5 instruments available
    Violin,
    /// 2 instruments available
    Viola,
    /// 3 instruments available
    Cello,
};

/** \struct String_Physical
 *  \brief Structure storing physical parameters of each string
 *
 *  B1 and B2 modal damping factors come from Demoucron's thesis, p. 78.
 *  and some ad-hoc experimentation.
 */
typedef struct {
    float T;  /**< \brief Tension          (N) */
    float L;  /**< \brief Length           (m) */
    float d;  /**< \brief Diameter         (m) */
    float pl; /**< \brief Linear Density   (kg/m) */
    float E;  /**< \brief Young's elastic modulus */
    float mu_s;
    float mu_d;
    float v0;
    float cutoff;
    unsigned int N;
    float rn[MAX_MODAL_DECAY_MODES];
} String_Physical;


#endif
