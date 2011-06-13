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

#include "artifastring/violin_string.h"
#include <math.h>
#include <stdlib.h> // for rand()

#ifdef DEBUG
#include <stdio.h>
#endif

const double FLOAT_EQUALITY_ABSOLUTE_ERROR = 1e-6;

ViolinString::ViolinString(String_Type_t which_string, int random_seed)
{
    // do NOT make this time(NULL); we want repeated
    // runs of the program to be identical!
    srand( random_seed );

    reset();

    set_physical_constants( string_params[which_string] );

#ifdef DEBUG
    time_seconds = 0.0;
#endif
}

ViolinString::~ViolinString() {
}

void ViolinString::reset()
{
    // init everything, just to be safe
    recache_pc_c = true;

    vpa_finger_x1 = 1.0;
    vpa_bow_x0 = 0.0;
    vpa_bow_force = 0.0;
    vpa_bow_velocity = 0.0;
    recache_vpa_c = true;

    vpa_pluck_force = 0.0;

    m_bow_slipping = false;
    m_active = false;
    m_y0dot_h = 0.0;
    m_y1_h = 0.0;
    m_string_excitation = 0.0;
    m_finger_dampening = 0.0;

    for (unsigned int n = 1; n <= MODES; ++n) {
        m_a[n-1] = 0.0;
        m_adot[n-1] = 0.0;
        m_a_h[n-1] = 0.0;
        m_adot_h[n-1] = 0.0;
    }
}

inline void ViolinString::calculate_eigens(double eigens[],
        const double position)
{
    // optimization from
    // http://groovit.disjunkt.com/analog/time-domain/fasttrig.html
    // except that w=b
    double y[2];
    const double x = M_PI*position;
    y[0] = sin(x);
    y[1] = 0.0;
    const double p = 2.0 * cos(x);
    unsigned int latest = 0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        y[latest] = p*y[!latest] - y[latest];
        eigens[n-1] = pc_c_sqrt_two_div_l * y[latest];
        latest = !latest;
    }
}

void ViolinString::finger(const double ratio_from_nut)
{
    const double ratio_from_bridge = 1.0 - ratio_from_nut;
    if (! (almostEquals(vpa_finger_x1, ratio_from_bridge)) ) {
        vpa_finger_x1 = ratio_from_bridge;
        recache_vpa_c = true;

        calculate_eigens(vpa_c_finger_eigens, vpa_finger_x1);
    }
}

void ViolinString::pluck(const double ratio_from_bridge,
                         const double pluck_force)
{
    vpa_pluck_force = pluck_force * PLUCK_FORCE_SCALE;
    m_active = true;
    if (! (almostEquals(vpa_bow_x0, ratio_from_bridge)) ) {
        vpa_bow_x0 = ratio_from_bridge;
        recache_vpa_c = true;

        calculate_eigens(vpa_c_bow_eigens, vpa_bow_x0);
    }
}


void ViolinString::bow(const double bow_ratio_from_bridge,
                       const double bow_force, const double bow_velocity)
{
    m_active = true;
    vpa_bow_force = bow_force;
    vpa_bow_velocity = bow_velocity;
    if (! (almostEquals(vpa_bow_x0, bow_ratio_from_bridge)) ) {
        vpa_bow_x0 = bow_ratio_from_bridge;
        recache_vpa_c = true;

        calculate_eigens(vpa_c_bow_eigens, vpa_bow_x0);
    }
}
String_Physical ViolinString::get_physical_constants()
{
    String_Physical pc_copy = pc;
    return pc_copy;
}

void ViolinString::set_physical_constants(String_Physical pc_new)
{
    pc = pc_new;
    recache_pc_c = true;
    recache_vpa_c = true;
}


void ViolinString::cache_pc_c()
{
    pc_c_sqrt_two_div_l = sqrt(2.0 / pc.L);

    const double div_pc_pl = 1.0 / pc.pl;
    const double pi_div_l = M_PI / pc.L;
    // text after eqn (2.5)
    const double I = M_PI * pc.d*pc.d*pc.d*pc.d / 64.0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        // text after eqn (2.5)
        const double n_pi_div_L = n*pi_div_l;
        const double w0n = sqrt( (pc.T * div_pc_pl) * n_pi_div_L*n_pi_div_L
                                 + ((pc.E * I * div_pc_pl)
                                    * n_pi_div_L*n_pi_div_L
                                    * n_pi_div_L*n_pi_div_L ));

        // text on p. 78
        const double r_n = pc.B1 + pc.B2*(n-1)*(n-1);

        // Other abbreviations
        const double w_n         = sqrt(w0n*w0n - r_n*r_n);
        const double theta_n     = w_n*dt;
        const double R_n         = exp(-r_n*dt);

        // Coefficients for calculation of new a
        X1[n-1] = (cos(theta_n) + (r_n/w_n)*sin(theta_n)) * R_n;
        X2[n-1] = (1.0 / w_n) * sin(theta_n) * R_n;
        X3[n-1] = (1.0 / (pc.pl * w0n*w0n)) * (1.0-X1[n-1]);

        // Coefficients for calculation of new a-dot
        Y1[n-1] = -((w_n + r_n*r_n / w_n) * sin(w_n*dt)) * R_n;
        Y2[n-1] = (cos(w_n*dt) - r_n/w_n * sin(w_n*dt)) * R_n;
        Y3[n-1] = -(1.0 / (w0n*w0n*pc.pl)) * Y1[n-1];

        // equation (2.35), with the sqrt inside the sum
        pc_c_bridge_forces[n-1] = pc_c_sqrt_two_div_l
                                  * (pc.T * n_pi_div_L
                                     + pc.E * I *
                                     n_pi_div_L*n_pi_div_L*n_pi_div_L);
    }
    calculate_eigens(vpa_c_finger_eigens, vpa_finger_x1);
    calculate_eigens(vpa_c_bow_eigens, vpa_bow_x0);
    recache_vpa_c = true;
    recache_pc_c = false;
}

void ViolinString::cache_vpa_c()
{
    if (recache_pc_c) {
        cache_pc_c();
    }

    double A01 = 0.0;
    double A11 = 0.0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        const double phix0 = vpa_c_bow_eigens[n-1];
        const double phix1 = vpa_c_finger_eigens[n-1];
        const double X3n = X3[n-1];
        A01 += phix1 * phix0 * X3n;
        A11 += phix1 * phix1 * X3n;
    }

    // eqn (2.28)
    vpa_c_C11 = -1.0 / A11;  // infinitely stiff spring
    vpa_c_C12 = A01 * vpa_c_C11;

    double B00 = 0.0;
    double B01 = 0.0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        const double phix0 = vpa_c_bow_eigens[n-1];
        const double phix1 = vpa_c_finger_eigens[n-1];
        const double Y3n = Y3[n-1];
        B00 += phix0 * phix0 * Y3n;
        B01 += phix0 * phix1 * Y3n;
    }

    vpa_c_C01 = 1.0 / (B00 + B01*vpa_c_C12);
    vpa_c_C02 = -B01*vpa_c_C11*vpa_c_C01;

    recache_vpa_c = false;
}


inline double ViolinString::tick()
{
    if (!m_active) {
        return 0.0;
    }
    if (recache_vpa_c) {
        cache_vpa_c();
    }
    compute_hist_modes();
    if (vpa_finger_x1) {
        compute_hist_finger();
    }
    // Calculate excitation force
    if (vpa_pluck_force != 0) {
        compute_hist_bow();
        m_string_excitation = compute_pluck();
    } else {
        if (vpa_bow_force != 0) {
            compute_hist_bow();
            m_string_excitation = compute_bow();
        } else {
            m_string_excitation = 0.0;
        }
    }
    m_finger_dampening = compute_finger();

    apply_forces();

    const double bridge_force = compute_bridge_force();

#ifdef DEBUG
    printf("%g\t%i\t%g\t%g\t%g\t%g\t%g\n", time_seconds, !m_bow_slipping,
           m_y0dot_h, m_string_excitation, m_finger_dampening,
           bridge_force, vpa_bow_force);
    time_seconds += dt;
#endif

    if ((vpa_bow_force == 0) && (vpa_pluck_force == 0)) {
        check_active(bridge_force);
    }
    return bridge_force;
}

inline void ViolinString::check_active(double bridge_force)
{
    if (fabs(bridge_force) < SUM_BELOW) {
        bool should_stop = true;
        for (unsigned int n = 1; n <= MODES; ++n) {
            if (fabs(m_adot[n-1]) >= EACH_MODAL_VELOCITY_BELOW) {
                should_stop = false;
                break;
            }
        }
        if (should_stop == true) {
            m_active = false;
        }
    }
}

void ViolinString::fill_buffer(double* buffer, const unsigned int num_samples)
{
    for (unsigned int i=0; i<num_samples; i++) {
        buffer[i] = tick();
    }
}

inline void ViolinString::compute_hist_modes()
{
    for (unsigned int n = 1; n <= MODES; ++n) {
        m_a_h[n-1]     = X1[n-1]*m_a[n-1] + X2[n-1]*m_adot[n-1];
        m_adot_h[n-1]  = Y1[n-1]*m_a[n-1] + Y2[n-1]*m_adot[n-1];
    }
}

inline void ViolinString::compute_hist_finger()
{
    m_y1_h = 0.0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        m_y1_h += m_a_h[n-1] * vpa_c_finger_eigens[n-1];
    }
}

inline void ViolinString::compute_hist_bow()
{
    m_y0dot_h = 0.0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        m_y0dot_h += m_adot_h[n-1] * vpa_c_bow_eigens[n-1];
    }
}

// a pluck is just a bow that disappears once it slips
inline double ViolinString::compute_pluck( )
{
    const double F0 = vpa_c_C01*(PLUCK_VELOCITY - m_y0dot_h) + vpa_c_C02*m_y1_h;
    if ( fabs(F0) > MU_PLUCK*vpa_pluck_force ) {
        vpa_pluck_force = 0.0;
    }
    return F0;
}

inline double ViolinString::compute_bow()
{
    // vpa_bow_force is not 0.0

    // special case: stationary string.  Assume stick.
    if (m_y0dot_h == 0) {
        m_bow_slipping = false;
    }

    if (!m_bow_slipping) {
        // is currently sticking

        // Has the maximum static force been exceeded yet?
        // eqn (2.31)
        const double F0 = vpa_c_C01*( vpa_bow_velocity - m_y0dot_h)
                          + vpa_c_C02*m_y1_h;
        // text after (2.31)
        if ( fabs(F0) > mu_s*vpa_bow_force ) {
            m_bow_slipping = true;
        }
        return F0;
    } else {
        // is currently slipping

        // add random noise
        const double ut = rand() / (double)RAND_MAX;
        const double N = 1.0 - A_noise * ut;

        double v_c;
        double f_c;
        if (vpa_bow_velocity != 0) {
            // normal, from (2.33, second part)
            v_c = (vpa_bow_velocity > 0.0) ? N*v0 : -N*v0;
            f_c = (vpa_bow_velocity > 0.0) ? vpa_bow_force : -vpa_bow_force;
        } else {
            // bow acts against any movement.
            v_c = (m_y0dot_h < 0.0) ? N*v0 : -N*v0;
            f_c = (m_y0dot_h < 0.0) ? vpa_bow_force : -vpa_bow_force;
        }

        // (2.34 exactly)
        const double div_v_c = 1.0 / v_c;
        const double c2 = -vpa_c_C01*div_v_c;
        const double c1 = (vpa_c_C01*((v_c - vpa_bow_velocity + m_y0dot_h))
                           + mu_d*f_c - vpa_c_C02*m_y1_h) * div_v_c;
        const double c0 = vpa_c_C01*(vpa_bow_velocity - m_y0dot_h)
                          + vpa_c_C02*m_y1_h - mu_s*f_c;
        const double Delta = c1*c1 - 4.0*c0*c2;

        if (Delta < 0.0) {
            // no real solutions for relative bow velocity:
            // bow has stuck to string, so bail out
            m_bow_slipping = false;
            return vpa_c_C01*(vpa_bow_velocity - m_y0dot_h) + vpa_c_C02*m_y1_h;
        } else {
            // bow might still slipping
            const double dv = (-c1 + sqrt(Delta))/(2.0*c2);

            // use v_c instead of vpa_bow_velocity so that
            // a stationary bow can still capture the string!
            if ((dv * v_c) > 0) {
                // bow starts sticking
                m_bow_slipping = false;
                return vpa_c_C01*(vpa_bow_velocity - m_y0dot_h) +
                       vpa_c_C02*m_y1_h;
            } else {
                // still slipping
                return vpa_c_C01*(dv + vpa_bow_velocity - m_y0dot_h)
                       + vpa_c_C02*m_y1_h;
            }
        }
    }
}


inline double ViolinString::compute_finger()
{
    if (vpa_finger_x1 != 0.0) {
        return vpa_c_C11 * m_y1_h  +  vpa_c_C12 * m_string_excitation;
    } else {
        return 0.0;
    }
}

inline void ViolinString::apply_forces()
{
    for (unsigned int n = 1; n <= MODES; ++n)
    {
        const double position_forces = vpa_c_bow_eigens[n-1]*m_string_excitation +
                                       vpa_c_finger_eigens[n-1]*m_finger_dampening;
        m_a[n-1] = m_a_h[n-1] + X3[n-1] * position_forces;
        m_adot[n-1] = m_adot_h[n-1] + Y3[n-1] * position_forces;
    }
}

inline double ViolinString::compute_bridge_force()
{
    // equation (2.35)
    double result = 0.0;
    for (unsigned int n = 1; n <= MODES; ++n) {
        result += m_a[n-1] * pc_c_bridge_forces[n-1];
    }
    return BRIDGE_AMPLIFY*result;
}

inline bool ViolinString::almostEquals(double one, double two)
{
    // maximum absolute error
    if (fabs(one-two) < FLOAT_EQUALITY_ABSOLUTE_ERROR) {
        return true;
    }
    // don't bother with relative error (yet?)
    return false;
}

