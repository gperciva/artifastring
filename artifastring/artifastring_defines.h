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
const int HAPTIC_DOWNSAMPLE_FACTOR = 1;
#endif

//const int ARTIFASTRING_INSTRUMENT_SAMPLE_RATE = 66150;
//const int ARTIFASTRING_INSTRUMENT_SAMPLE_RATE = 44100;
const int HAPTIC_SAMPLE_RATE = ARTIFASTRING_INSTRUMENT_SAMPLE_RATE / HAPTIC_DOWNSAMPLE_FACTOR;
//const int HAPTIC_DOWNSAMPLE_FACTOR = 8;
//const int HAPTIC_SAMPLE_RATE = ARTIFASTRING_SAMPLE_RATE / HAPTIC_DOWNSAMPLE_FACTOR;

//const int NORMAL_BUFFER_SIZE = 1024;
const int NORMAL_BUFFER_SIZE = 441;

//const float float_to_int = 0.001 * std::numeric_limits<int>::max();
const double string_float_to_int = 0.001*((1 << 30)-1);
const double string_int_to_float = 1.0 / string_float_to_int;

/**
 * \enum InstrumentType
 * \brief foogle
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
 *  For more information, see my PhD dissertation.
 */
typedef struct {
    float T;  /**< \brief Tension          (N) */
    float L;  /**< \brief Length           (m) */
    float d;  /**< \brief Diameter         (m) */
    float pl; /**< \brief Linear Density   (kg/m) */
    float E;  /**< \brief Young's elastic modulus */
    float mu_s; /**< \brief Coefficient of static friction */
    float mu_d; /**< \brief Coefficient of dynamic friction */
    float v0; /**< \brief Slope of hyperbolic friction curve */
    float cutoff; /**< \brief Minimum sum-of-squares amplitude to maintain processing */
    unsigned int N; /**< \brief Number of modes for this string (should be a multiple of 4 for SSE, or 8 for AVX) */
    float rn[MAX_MODAL_DECAY_MODES]; /**< Array of modal decays */
} String_Physical;


#endif
