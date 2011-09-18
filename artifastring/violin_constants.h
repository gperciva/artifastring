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

const double PLUCK_FORCE_SCALE = 1e0;
const double BRIDGE_AMPLIFY = 1e-2;

const int MODES = 60;

// optimization for "turning off" a string which is barely vibrating.
const double SUM_BELOW = 1e-6;
const double EACH_MODAL_VELOCITY_BELOW = 1e-4;


/**
 * \brief enumeration type to access string physical constants
 */
enum String_Type_t {vl_G, vl_D, vl_A, vl_E};

// friction constants
const double mu_s = 0.8;
const double mu_d = 0.3;
const double v0 = 0.1; // Demoucron's estimate intuition and/or listening

// pluck constants, estimated from listening
const double PLUCK_VELOCITY = 0.1; // in m/s
const double MU_PLUCK = 1.0;

// noise
const double A_noise = 0.05; // estimated from listening

// time length of each sample, in seconds
const int VIOLIN_SAMPLE_RATE = 44100;
const double dt = 1.0 / VIOLIN_SAMPLE_RATE;


/** \struct String_Physical
 *  \brief Structure storing physical parameters of each string
 *
 *  B1 and B2 modal damping factors come from Demoucron's thesis, p. 78.
 *  and some ad-hoc experimentation.
 */
typedef struct {
    double T;  /**< \brief Tension          (N) */
    double L;  /**< \brief Length           (m) */
    double d;  /**< \brief Diameter         (m) */
    double pl; /**< \brief Linear Density   (kg/m) */
    double E;  /**< \brief Young's elastic modulus */
    // FIXME: remove B1 and B2
    double B1; /**< \brief modal dampening factor; r_n = B1 + B2*(n-1)*(n-1); */
    double B2; /**< \brief modal dampening factor; r_n = B1 + B2*(n-1)*(n-1); */
    double modes[MODES];
} String_Physical;

const String_Physical string_params[] = {
    /* Violin G string */
    {   /* T= */ 44.6,  /* l= */ 0.325, /* d= */ 0.79e-3,
        /* pl= */ 2.66e-3,
        /* E= */ 4.0e9,
        2.0, 7.0, // extra resonance
        #include "violin_g_modes.h"
    },

    /* Violin D string */
    {   /* T= */ 34.8,  /* l= */ 0.325, /* d= */ 0.63e-3,
        /* pl= */ 0.92e-3,
        /* E= */ 4.0e9,
        3.12, 7.0,
        #include "violin_d_modes.h"
    },

    /* Violin A string */
    {   /* T= */ 50.0,  /* l= */ 0.325, /* d= */ 0.52e-3,
        /* pl= */ 0.59e-3,
        /* E= */ 4.0e9,
        3.12, 7.0,
        #include "violin_a_modes.h"
    },

    /* Violin E string */
    {   /* T= */ 72.6,  /* l= */ 0.325, /* d= */ 0.30e-3,
        /* pl= */ 0.38e-3,
        /* E= */ 4.0e9,
        4.0, 7.0, // B1 "should be a big greater"
        #include "violin_e_modes.h"
    },
};


#endif

