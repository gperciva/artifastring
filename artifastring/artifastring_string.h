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

#ifndef ARTIFASTRING_STRING_H
#define ARTIFASTRING_STRING_H

//#define DEBUG

#include "artifastring/artifastring_constants.h"

#include <Eigen/Core>
//#include <Eigen/QR>

#ifdef RESEARCH
// for log file
#include <stdio.h>
#endif

// Artifastring Array
typedef Eigen::Array<float, MODES, 1> AA;
//typedef Eigen::Matrix<float, MODES, 1> AA;

enum ExternalActionsType {
    OFF, RELEASE, PLUCK, BOW, BOW_ACCEL
};


struct StringConstants {
    AA X1; // displacement
    AA X2;
    AA X3;
    AA Y1; // velocity
    AA Y2;
    AA Y3;
    AA G; // bridge
    float div_pc_L;
    float sqrt_two_div_L;
};

struct ViolinistCoefficients {
    float x0;
    float x1;
    float x2;
    AA phix0; // position eigenvalues
    AA phix1;
    AA phix2;

    //float D1old, D2old, D3old, D4old; // pluck and release
    float D1, D2, D3, D4; // bow
    float D5, D6, D7; // finger during bowing

    float D8, D9, D10, D11; // pluck release

    // extra "actions"
    float K0;
    float K1;
    float K2;
    float R0;
    float R1;
    float R2;
    float y_pluck; // for pluck displacement
    float y_pluck_target;
    int pluck_samples_remaining;
    bool recache;
};

struct ViolinistActions {
    float bow_pluck_position;  // bow/pluck position
    float finger_position;  // finger position
    float Fb;  // bow force
    float vb;  // bow velocity
    // iffy actions
    float va;  // bow acceleration, per dt (unit of time)
    float vb_target; // target bow velocity, used in acceleration
    float Kf;
};

struct StringState {
    AA a;
    AA ad;
    int slipstate;
    ExternalActionsType actions;
};


/// \brief Modal synthesis of a violin string.
class ArtifastringString {
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW
    /**
     * \brief Constructor
     * @param[in] which_instrument The member of the violin family to
     * simulate.  See \ref InstrumentType
     * @param[in] instrument_number The instrument number within the family.
     * See \ref InstrumentType
     * @param[in] string_number The string (higher numbers are
     * higher strings).  This values is also used to initializes
     * the randomness (for added noise in the model).
     * @param[in] fs_multiplication_factor This sets the sampling
     * rate of the string by multiplying the base instrument
     * sampling rate.
     */
    ArtifastringString(InstrumentType which_instrument,
                       int instrument_number, int string_number,
                       int fs_multiplication_factor);
    /// \brief Destructor; nothing special
    ~ArtifastringString();
    /// \brief Stops all movement
    void reset();


    /** \brief Places finger on the string.
     *
     * Finger remains in place until moved.
     * @param[in] ratio_from_nut Measured as a fraction of string
     * length.
     * @param[in] Kf_get This sets how firmly the finger is
     * pressed against the string.  1,0 indicates normal finger
     * strength, while 0.0001 indicates a very light finger
     * suitable for playing harmonic notes.
     */
    void finger(const float ratio_from_nut, const float Kf_get=1.0);

    /** \brief Plucks a string.
     *
     * The pluck is simulated like a bow that pulls until
     * it slips for the first time; as a result, you cannot
     * predict when the pluck has finished "starting".
     * @param[in] ratio_from_bridge Measured as a fraction of
     * string length.
     * @param[in] pull_distance Measured in units of 5mm.  This
     * number was chosen so that a normal pluck on the violin uses
     * a pull distance of 1.0.  0.0 produces no pluck at all.
     */
    void pluck(const float ratio_from_bridge, const float pull_distance=1.0);

    /** \brief Sets the bow's action.
     *
     * Bow actions are assumed to continue until changed.
     * @param[in] bow_ratio_from_bridge Measured as a fraction of
     * string length.
     * @param[in] bow_force Measured in Newtons.
     * @param[in] bow_velocity Measured in meters / second.
     */
    void bow(const float bow_ratio_from_bridge,
             const float bow_force, const float bow_velocity);
    void bow_accel(const float bow_ratio_from_bridge,
                   const float bow_force, const float bow_velocity_target,
                   const float bow_accel);


    /** \brief Advances time and writes data to a buffer.
     * @param[out] *buffer Place to write output.
     * @param[in] num_samples Number of samples to advance.
     * @warning You are responsible for allocating sufficient
     * memory for the buffer.
     */
    void fill_buffer(float* buffer, const int num_samples);

    void fill_buffer_forces(float* buffer, float* forces,
                            const int num_samples);


    /** \brief Returns the string physical constants.
     *
     * This method is not recommended for normal use; it is merely
     * a curiosity for people wanting to experiment.
     */
    String_Physical get_physical_constants();

    /** \brief Sets the string physical constants.
     *
     * This method is not recommended for normal use; it is merely
     * a curiosity for people wanting to experiment.
     * @param[in] pc_new String physical constants.
     */
    void set_physical_constants(String_Physical pc_new);

#ifdef RESEARCH
    bool set_logfile(const char *filename);
    void logfile_data();
    int get_num_skips() {
        return num_skips;
    };
#endif

    void string_release();

protected:
    // physical constants
    String_Physical pc;

    // calculated from physical constants
    void cache_pc_c();

    inline void setup_vc_positions();
    inline void cache_pa_c();

    // calculated (almost) all the time
    float tick_pluck();
    float tick_release();
    float tick_free();
    float tick_bow();
    float tick_output_force;

    void update_pluck_actions();
    void update_bow_accel();
    inline float compute_bow(const float v0h, const float y1h,
                             const float v1h);

    // returns INFINITY if not valid
    inline float compute_bow_force(const float v0h, const float y1h,
                                   const float v1h, const float dv);
    inline float compute_bow_slip_negative(const float v0h, const float y1h,
                                           const float v1h);
    inline float compute_bow_slip_positive(const float v0h, const float y1h,
                                           const float v1h);

    // actual output of model
    inline float compute_bridge_force();

    // floating-point equality
    inline bool abs_le(const float one, const float two);
    inline bool almostEquals(float one, float two);

    int num_friction_skip_over_stick;
#ifdef RESEARCH
    FILE *logfile;
    float time_seconds;

    void logfile_close();
    float m_v0h;
    float m_dv;
    float m_F0;
    int m_skip;
    int num_skips;
#endif
    int debug_ticks;
    int debug_string_num;


    StringConstants sc;
    ViolinistCoefficients vc;
    StringState ss;
    ViolinistActions va;

    //Eigen::ColPivHouseholderQR<Eigen::Matrix3f> qr;
    //Eigen::HouseholderQR<Eigen::Matrix3f> qr;
    //Eigen::LLT<Eigen::Matrix3f> qr;
    Eigen::Matrix3f inv_A;
    Eigen::Matrix2f inv_A_release;
    //Eigen::ColPivHouseholderQR<Eigen::Matrix2f> qr2;

    int plucks;

    int fs_multiplier;
    int fs;
    float dt;

    //Eigen::Array<float, Eigen::Dynamic, 1> *audio_samples;
    // maximum size of this buffer
    //Eigen::Array<float, NORMAL_BUFFER_SIZE*3, 1> audio_samples;
    //Eigen::Array<float, NORMAL_BUFFER_SIZE*3, 1> force_samples;
    float audio_samples[NORMAL_BUFFER_SIZE*3];
    float force_samples[NORMAL_BUFFER_SIZE*3];
};
#endif

