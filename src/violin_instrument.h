/*
 * Copyright 2010 Graham Percival
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

#include "violin_string.h"
#include "violin_body_impulse.h"

//#define NO_CONVOLUTION
#ifdef NO_CONVOLUTION
const double NO_CONVOLUTION_AMPLIFY = 20.0;
#endif

const unsigned int NORMAL_BUFFER_SIZE = 512;
const unsigned int BRIDGE_BUFFER_SIZE = 1024; // string + impulse size

/// \brief Main class for violin synthesis  (if in doubt, use this one)
class ViolinInstrument {
public:
    /**
     * \brief Constructor
     * @param[in] random_seed Initializes the randomness (for added
     * noise in the model).
     */
    ViolinInstrument(int random_seed=0);
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
    void finger(int which_string, double ratio_from_nut);

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
    void pluck(int which_string, double ratio_from_bridge,
               double pluck_force);

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
    void bow(int which_string, double bow_ratio_from_bridge,
             double bow_force, double bow_velocity);

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
    void wait_samples(short *buffer, unsigned int num_samples);


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
    ViolinString *violinString[4];
    double violin_string_buffer[4][NORMAL_BUFFER_SIZE];

    // only does up to NORMAL_BUFFER_SIZE !
    void handle_buffer(short output[], unsigned int num_samples);

    double bridge_buffer[BRIDGE_BUFFER_SIZE];
    unsigned int bridge_write_index;
    unsigned int bridge_read_index;

    double f_hole[NORMAL_BUFFER_SIZE];
    void body_impulse(unsigned int num_samples);

};

#endif

