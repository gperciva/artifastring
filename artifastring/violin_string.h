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

#ifndef VIOLIN_STRING
#define VIOLIN_STRING

//#define DEBUG

#include "artifastring/violin_constants.h"

/// \brief Modal synthesis of a violin string.
class ViolinString {
public:
    /**
     * \brief Constructor
     * @param[in] which_string The violin string to simulate.
     * @param[in] random_seed Initializes the randomness (for added
     * noise in the model).
     */
    ViolinString(String_Type_t which_string, int random_seed=0);
    /// \brief Destructor; nothing special
    ~ViolinString();
    /// \brief Stops all movement
    void reset();


    /** \brief Places finger on the string.
     *
     * Finger remains in place until moved.
     * @param[in] ratio_from_nut Measured as a fraction of string
     * length.
     */
    void finger(const double ratio_from_nut);

    /** \brief Plucks a string.
     *
     * The pluck is simulated like a bow that pulls until
     * it slips for the first time; as a result, you cannot
     * predict when the pluck has finished "starting".
     * @param[in] ratio_from_bridge Measured as a fraction of
     * string length.
     * @param[in] pluck_force Measured in 0.0 to 1.0 (ARBITRARY).
     * @todo Re-think the pluck force paramater + constants
     */
    void pluck(const double ratio_from_bridge, const double pluck_force);

    /** \brief Sets the bow's action.
     *
     * Bow actions are assumed to continue until changed.
     * @param[in] bow_ratio_from_bridge Measured as a fraction of
     * string length.
     * @param[in] bow_force Measured in Newtons.
     * @param[in] bow_velocity Measured in meters / second.
     */
    void bow(const double bow_ratio_from_bridge,
             const double bow_force, const double bow_velocity);


    /** \brief Advances time and writes data to a buffer.
     * @param[out] *buffer Place to write output.
     * @param[in] num_samples Number of samples to advance.
     * @warning You are responsible for allocating sufficient
     * memory for the buffer.
     */
    void fill_buffer(double* buffer, const unsigned int num_samples);


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

protected:
#ifdef DEBUG
    double time_seconds;
#endif

    // physical constants
    String_Physical pc;

    // optimized shared function
    inline void calculate_eigens(double eigens[], const double position);


    // calculated from physical constants
    double pc_c_sqrt_two_div_l;
    double pc_c_bridge_forces[MODES];
    double X1[MODES], X2[MODES], X3[MODES];
    double Y1[MODES], Y2[MODES], Y3[MODES];
    bool recache_pc_c;
    void cache_pc_c();


    // violinist physical actions
    double vpa_finger_x1;      // measured in ratio from bridge
    double vpa_pluck_force;    // measured in ARBITRARY
    double vpa_bow_x0;         // measured in ratio from bridge
    double vpa_bow_force;      // measured in newtons
    double vpa_bow_velocity;   // measured in meters per second

    // calculated from violinist physical actions (en masse)
    double vpa_c_C11;
    double vpa_c_C12;
    double vpa_c_C01;
    double vpa_c_C02;
    bool recache_vpa_c;
    void cache_vpa_c();

    // calculated from violinist physical actions (independently)
    double vpa_c_finger_eigens[MODES];
    double vpa_c_bow_eigens[MODES];


    // calculated (almost) all the time
    double tick();

    // do we need to calculate anything?
    bool m_active;
    inline void check_active(const double bridge_force);

    // "historical" calculations
    // modal arrays: m_a m_adot m_a_h m_adot_h
    double m_a_h[MODES];    // "historical" displacement
    double m_adot_h[MODES]; // "historical" velocity
    inline void compute_hist_modes();
    // calculates m_y1_h
    double m_y1_h;
    inline void compute_hist_finger();
    // calculates m_y0dot_h
    double m_y0dot_h;
    inline void compute_hist_bow();
    // F0 and F1
    double m_string_excitation;
    double m_finger_dampening;

    // how should we differ from the "historical" values?
    inline double compute_finger();
    inline double compute_pluck();
    bool m_bow_slipping;
    inline double compute_bow();

    // values for the "next step"
    double m_a[MODES];      // displacement
    double m_adot[MODES];   // velocity
    inline void apply_forces();

    // actual output of model
    inline double compute_bridge_force();

    // floating-point equality
    inline bool almostEquals(double one, double two);
};
#endif

