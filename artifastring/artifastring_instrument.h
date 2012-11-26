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

#ifndef ARTIFASTRING_INSTRUMENT_H
#define ARTIFASTRING_INSTRUMENT_H

#include "artifastring/artifastring_defines.h"
#include "artifastring/artifastring_constants.h"
#include "artifastring/fft_convolution.h"

class ArtifastringString;

const int NUM_VIOLIN_STRINGS = 4;
const int NUM_MULTIPLIERS = 4;


/// \brief Main class for violin synthesis  (if in doubt, use this one)
class ArtifastringInstrument {
public:
    /**
     * \brief Constructor
     * @param[in] instrument_type The member of the violin family to
     * simulate.  See \ref InstrumentType
     * @param[in] instrument_number The instrument number within the family.
     * See \ref InstrumentType
     */
    ArtifastringInstrument(InstrumentType instrument_type=Violin,
                           int instrument_number=0);
    /// \brief Destructor; nothing special
    ~ArtifastringInstrument();
    /// \brief Stops all movement
    void reset();

    /** \brief Places finger on the string.
     *
     * Finger remains in place until moved.
     * @param[in] which_string Instrument string (0,1,2,3); higher
     * string numbers are higher in pitch.  0 is the G string).
     * @param[in] ratio_from_nut Measured as a fraction of string
     * length.
     * @param[in] Kf This sets how firmly the finger is
     * pressed against the string.  1,0 indicates normal finger
     * strength, while 0.0001 indicates a very light finger
     * suitable for playing harmonic notes.
     */
    void finger(int which_string, float ratio_from_nut, float Kf=1.0);

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

    void bow_accel(int which_string, float bow_ratio_from_bridge,
                   float bow_force, float bow_velocity_target,
                   float bow_accel);

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
    int wait_samples(short *buffer, int num_samples);

    int wait_samples_forces(short *buffer, short *forces, int num_samples);
    int wait_samples_forces_python(
        short *buffer, int num_samples,
        short *forces, int num_samples2);

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

#ifdef RESEARCH
    bool set_string_logfile(int which_string, const char *filename);
    int get_num_skips(int which_string);

    /** \brief Get the internal string output pre-instrument body
     *
     * WARNING: you must allocate enough buffer space to hold
     * the data.  This can be up to 4* the hop size!
     * it will return the actual size used
     */
    int get_string_buffer(int which_string, float *buffer, int num_samples);
#endif

private:
    ArtifastringString *artifastringString[NUM_VIOLIN_STRINGS];
    float violin_string_buffer[NUM_VIOLIN_STRINGS][NORMAL_BUFFER_SIZE*NUM_MULTIPLIERS];

    ArtifastringConvolution *audio_convolution[NUM_MULTIPLIERS];
    ArtifastringConvolution *haptic_convolution[NUM_MULTIPLIERS];
    float *string_audio_output[NUM_MULTIPLIERS];
    float *string_haptic_output[NUM_MULTIPLIERS];

    InstrumentType m_instrument_type;

    // only does up to NORMAL_BUFFER_SIZE !
    void handle_buffer(short output[], short forces[], int num_samples);

    float *body_in;
    float *body_out;
    float *f_hole; // output of body convolution
    int f_hole_read_index;

    float *bow_string_forces;
    float *bow_fft_output;
    float *bow_convolution_output;
    int bow_convolution_read_index;
    int bow_string;

    // fftwf_complex
    void *kernel_interim;
    void *body_interim;
    void *forces_interim;
    // fftwf_plan
    void *body_plan_f_p;
    void *body_plan_b_p;
    void *forces_plan_f_p;
    void *forces_plan_b_p;
    int forces_M;
    int body_M;

    float m_bridge_force_amplify;
    float m_bow_force_amplify;

};

#endif

