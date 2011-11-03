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


#ifndef ARTIFASTRING_CONSTANTS
#define ARTIFASTRING_CONSTANTS

#include "artifastring_defines.h"

/**
 * \file artifastring_constants.h
 * \brief Physical constants used in artifastring
 */

// time length of each sample, in seconds
//const float dt = 1.0f / ARTIFASTRING_SAMPLE_RATE;


const float BRIDGE_FORCE_AMPLIFY [] = {1e-2f, 1e-1f, 1e-2f};
//const float BRIDGE_FORCE_AMPLIFY [] = {1e-3f, 1e-2f, 3e-3f};
const float BOW_FORCE_AMPLIFY [] = {1e-1f, 1e-1f, 1e-1f};


const int FS_MULTIPLICATION_FACTOR[3][4] = {
    {2,2,4,4},
    {2,2,2,4},
    {1,2,2,2},
};



// pluck constants, estimated from listening
const float PLUCK_VELOCITY = 0.1f; // in m/s
const float PLUCK_DISPLACEMENT = 0.005f; // in m
const float PLUCK_SECONDS = 0.1f; // in seconds

const float K_FINGER = 1e5f;
const float R_FINGER = 30.0f;
const float K_PLUCK  = 1e4f;
const float R_PLUCK  = 1e1f;

const float PLUCK_WIDTH = 0.012f; // m
const float FINGER_WIDTH = 0.01f; // m

// noise
//const float A_noise = 0.05f; // estimated from listening
const float A_noise = 0.02f; // estimated from listening
//const float A_noise = 0.0f; // estimated from listening

//#ifdef RESEARCH
//const int MODES = 32;
//#else
//#endif
//const int MODES = 32; // keep this a multiple of four for SIMD!
const int MODES = 40; // keep this a multiple of four for SIMD!


// string physical constants
#include "constants/strings_violin.h"
#include "constants/strings_viola.h"
#include "constants/strings_cello.h"

#endif

