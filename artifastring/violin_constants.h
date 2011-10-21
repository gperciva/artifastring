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


#ifndef VIOLIN_CONSTANTS
#define VIOLIN_CONSTANTS

/**
 * \file violin_constants.h
 * \brief Physical constants of a violin.
 */

/**
 * \brief enumeration type to access string physical constants
 */
enum InstrumentType {
    Violin, Viola, Cello,
};

const float PLUCK_FORCE_SCALE = 1e0;
const float BRIDGE_FORCE_AMPLIFY [] = {1e-2, 2e-3, 2e-3};

const int MODES = 60;

// optimization for "turning off" a string which is barely vibrating.
const float SUM_BELOW = 1e-6;
const float EACH_MODAL_VELOCITY_BELOW = 1e-4;


// friction constants
const float inst_mu_s[] = { 0.8, 0.8, 1.0 };
const float inst_mu_d[] = { 0.3, 0.3, 0.4 };
const float v0 = 0.1; // Demoucron's estimate intuition and/or listening

// pluck constants, estimated from listening
const float PLUCK_VELOCITY = 0.1; // in m/s
const float MU_PLUCK = 1.0;

// noise
const float A_noise = 0.05; // estimated from listening

// time length of each sample, in seconds
const int VIOLIN_SAMPLE_RATE = 44100;
const float dt = 1.0 / VIOLIN_SAMPLE_RATE;


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
    // FIXME: remove B1 and B2
    float B1; /**< \brief modal dampening factor; r_n = B1 + B2*(n-1)*(n-1); */
    float B2; /**< \brief modal dampening factor; r_n = B1 + B2*(n-1)*(n-1); */
    float modes[MODES];
} String_Physical;

const String_Physical string_params[][4] = {
    {
        /* Violin G string */
        {   /* T= */ 41.8,
            /* l= */ 0.325,
            /* d= */ 0.79e-3,
            /* pl= */ 2.61e-3,
            /* E= */ 4.0e9,
            2.0, 7.0, // extra resonance
#include "violin_g_modes.h"
        },
        /* Violin D string */
        {   /* T= */ 46.6,
            /* l= */ 0.325,
            /* d= */ 0.63e-3,
            /* pl= */ 1.28e-3,
            /* E= */ 4.09,
            3.12, 7.0,
#include "violin_d_modes.h"
        },
        /* Violin A string */
        {   /* T= */ 55.3,
            /* l= */ 0.325,
            /* d= */ 0.62e-3,
            /* pl= */ 0.67e-3,
            /* E= */ 4.0e9,
            3.12, 7.0,
#include "violin_a_modes.h"
        },
        /* Violin E string */
        {   /* T= */ 81.2,
            /* l= */ 0.328,
            /* d= */ 0.30e-3,
            /* pl= */ 0.43e-3,
            /* E= */ 200.0e9,
            5.0, 8.0, // B1 "should be a big greater"
#include "violin_e_modes.h"
        },
    },

    {
        /* Viola C string */
        {   /* T= */ 52.0,
            /* l= */ 0.37,
            /* d= */ 0.99e-3,
            /* pl= */ 5.63e-3,
            /* E= */ 4.0e9,
            2.0, 7.0, // extra resonance
#include "violin_g_modes.h"
        },
        /* Viola G string */
        {   /* T= */ 51.8,
            /* l= */ 0.37,
            /* d= */ 0.89e-3,
            /* pl= */ 2.5e-3,
            /* E= */ 4.0e9,
            2.0, 7.0, // extra resonance
#include "violin_g_modes.h"
        },
        /* Viola D string */
        {   /* T= */ 53.6,
            /* l= */ 0.37,
            /* d= */ 0.83e-3,
            /* pl= */ 1.12e-3,
            /* E= */ 4.0e9,
            3.12, 7.0,
#include "violin_d_modes.h"
        },
        /* Viola A string */
        {   /* T= */ 80.1,
            /* l= */ 0.37,
            /* d= */ 0.62e-3,
            /* pl= */ 0.74e-3,
            /* E= */ 4.0e9,
            3.12, 7.0,
#include "violin_a_modes.h"
        },
    },

    {
        /* Cello C string */
        {   /* T= */ 123.0,
            /* l= */ 0.682,
            /* d= */ 1.68e-3,
            /* pl= */ 15.66e-3,
            /* E= */ 4.0e9,
            4.0, 7.0,
#include "cello_c_modes.h"
        },
        /* Cello G string */
        {   /* T= */ 122.7,
            /* l= */ 0.682,
            /* d= */ 1.12e-3,
            /* pl= */ 6.97e-3,
            /* E= */ 4.0e9,
            2.0, 7.0,
#include "cello_g_modes.h"
        },
        /* Cello D string */
        {   /* T= */ 128.4,
            /* l= */ 0.682,
            /* d= */ 0.98e-3,
            /* pl= */ 3.26e-3,
            /* E= */ 4.0e9,
            3.12, 7.0,
#include "cello_d_modes.h"
        },
        /* Cello A string */
        {   /* T= */ 153.8,
            /* l= */ 0.682,
            /* d= */ 0.65e-3,
            /* pl= */ 1.71e-3,
            /* E= */ 4.0e9,
            3.0, 7.0,
#include "cello_a_modes.h"
        },
    }
};

#endif

