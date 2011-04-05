
#ifndef VIOLIN_CONSTANTS
#define VIOLIN_CONSTANTS

/**
 * \file violin_constants.h
 * \brief Physical constants of a violin.
 */

const double PLUCK_FORCE_SCALE = 1e0;
const double BRIDGE_AMPLIFY = 1e-2;

const unsigned int MODES = 56;

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
const double dt = 1.0 / 44100.0;


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
    double B1; /**< \brief modal dampening factor; r_n = B1 + B2*(n-1)*(n-1); */
    double B2; /**< \brief modal dampening factor; r_n = B1 + B2*(n-1)*(n-1); */
} String_Physical;

const String_Physical string_params[] = {
    /* Violin G string */
    {   /* T= */ 44.6,  /* l= */ 0.33, /* d= */ 0.8e-3,
        /* pl= */ 2.66e-3,
        /* E= */ 4.0e9,
        2.0, 7.0, // extra resonance
    },

    /* Violin D string */
    {   /* T= */ 34.8,  /* l= */ 0.33, /* d= */ 0.8e-3,
                 /* pl= */ 0.92e-3,
                 /* E= */ 4.0e9,
                 3.12, 7.0,
    },

    /* Violin A string */
    {   /* T= */ 50.0,  /* l= */ 0.33, /* d= */ 0.56e-3,
                 /* pl= */ 0.59e-3,
                 /* E= */ 4.0e9,
                 3.12, 7.0,
    },

    /* Violin E string */
    {   /* T= */ 72.6,  /* l= */ 0.33, /* d= */ 0.31e-3,
                 /* pl= */ 0.38e-3,
                 /* E= */ 4.0e9,
                 4.0, 7.0, // B1 "should be a big greater"
    },
};


#endif
