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

#ifndef VIOLIN_INSTRUMENT
#define VIOLIN_INSTRUMENT

#include "artifastring/violin_constants.h"
#include "artifastring/violin_body_impulse.h"

class ViolinString;

const int NUM_VIOLIN_STRINGS = 4;

// size optimization: allows for AND-based ring buffers
const int NORMAL_BUFFER_SIZE = PC_KERNEL_SIZE/2; // is 1024
const int CONVOLUTION_ACTUAL_DATA_SIZE = NORMAL_BUFFER_SIZE + PC_KERNEL_SIZE;

// round (NORMAL_BUFFER_SIZE+PC_KERNEL_SIZE) to next power of 2
// can't be bothered to write math for this; I'm only doing it once.
const int CONVOLUTION_SIZE = 4096;
const int F_HOLE_SIZE = 4096;

/// \brief Main class for violin synthesis  (if in doubt, use this one)
class ViolinInstrument {
public:
    /**
     * \brief Constructor
     * @param[in] instrument_number Selects instrument (see
     * documentation); values above the maximum instrument are
     * reduced with modulus (to select the instrument) but will
     * still initialize the randomness (for added noise in the
     * string model).
     */
    ViolinInstrument(int instrument_number=0);
    /// \brief Destructor; nothing special
    ~ViolinInstrument();
    /// \brief Stops all movement
    void reset();

    /** \brief Places finger on the string.
     *
     * Finger remains in place until moved.
     * @param[in] which_string Instrument string (0,1,2,3); higher
     * string numbers are higher in pitch.  0 is the G string).
     * @param[in] ratio_from_nut Measured as a fraction of string
     * length.
     */
    void finger(int which_string, float ratio_from_nut);

    /** \brief Plucks a string.
     *
     * The pluck is simulated like a bow that pulls until
     * it slips for the first time; as a result, you cannot
     * predict when the pluck has finished "starting".
     * @param[in] which_string Instrument string (0,1,2,3); higher
     * string numbers are higher in pitch.  0 is the G string).
     * @param[in] ratio_from_bridge Measured as a fraction of
     * string length.
     * @param[in] pluck_force Measured in 0.0 to 1.0 (ARBITRARY).
     * @todo Re-think the pluck force paramater + constants
     */
    void pluck(int which_string, float ratio_from_bridge,
               float pluck_force);

    /** \brief Sets the bow's action.
     *
     * Bow actions are assumed to continue until changed.
     * @param[in] which_string Instrument string (0,1,2,3); higher
     * string numbers are higher in pitch.  0 is the G string).
     * @param[in] bow_ratio_from_bridge Measured as a fraction of
     * string length.
     * @param[in] bow_force Measured in Newtons.
     * @param[in] bow_velocity Measured in meters / second.
     */
    void bow(int which_string, float bow_ratio_from_bridge,
             float bow_force, float bow_velocity);

    /** \brief Advances time and writes data to a buffer.
     *
     * Recommended: use MonoWav to get the short *buffer if you
     * want to write a wav file.  For realtime use, figure out the
     * buffer on your own.  :)
     * @param[out] *buffer Place to write output.
     * @param[in] num_samples Number of samples to advance.
     * @warning You are responsible for allocating sufficient
     * memory for the buffer.
     */
    void wait_samples(short *buffer, int num_samples);

    void wait_samples_forces(short *buffer, short *forces, int num_samples);

    /** \brief Returns a string's physical constants.
     *
     * This method is not recommended for normal use; it is merely
     * a curiosity for people wanting to experiment.
     * @param[in] which_string Instrument string (0,1,2,3); higher
     * string numbers are higher in pitch.  0 is the G string).
     */
    String_Physical get_physical_constants(int which_string);

    /** \brief Sets a string's physical constants.
     *
     * This method is not recommended for normal use; it is merely
     * a curiosity for people wanting to experiment.
     * @param[in] which_string Instrument string (0,1,2,3); higher
     * string numbers are higher in pitch.  0 is the G string).
     * @param[in] pc_new String physical constants.
     */
    void set_physical_constants(int which_string, String_Physical pc_new);

private:
    ViolinString *violinString[NUM_VIOLIN_STRINGS];
    float violin_string_buffer[NUM_VIOLIN_STRINGS][NORMAL_BUFFER_SIZE];

    // only does up to NORMAL_BUFFER_SIZE !
    void handle_buffer(short output[], short forces[], int num_samples);

    void body_impulse();
    float *body_in;
    float *body_out;
    float f_hole[F_HOLE_SIZE];
    int f_hole_read_index;

    float bow_string_forces[NORMAL_BUFFER_SIZE];
    int bow_string;

    // fftwf_complex
    void *kernel_interim;
    void *body_interim;
    // fftwf_plan
    void *body_plan_f_p;
    void *body_plan_b_p;
    int body_M;

    float m_bridge_force_amplify;
    float m_bow_force_amplify;
};

#endif

