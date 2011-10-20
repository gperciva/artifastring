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

const float FLOAT_EQUALITY_ABSOLUTE_ERROR = 1e-6;

ViolinString::ViolinString(InstrumentType which_instrument, int string_number)
{
    // do NOT make this time(NULL); we want repeated
    // runs of the program to be identical!
    srand( string_number );

    reset();

    set_physical_constants( string_params[which_instrument][string_number] );
    set_bow_friction(inst_mu_s[which_instrument], inst_mu_d[which_instrument]);

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

    for (int n = 1; n <= MODES; ++n) {
        m_a[n-1] = 0.0;
        m_adot[n-1] = 0.0;
        m_a_h[n-1] = 0.0;
        m_adot_h[n-1] = 0.0;
    }
}

inline void ViolinString::calculate_eigens(float eigens[],
        const float position)
{
    // optimization from
    // http://groovit.disjunkt.com/analog/time-domain/fasttrig.html
    // except that w=b
    float y[2];
    const float x = M_PI*position;
    y[0] = sin(x);
    y[1] = 0.0;
    const float p = 2.0 * cos(x);
    int latest = 0;
    for (int n = 1; n <= MODES; ++n) {
        y[latest] = p*y[!latest] - y[latest];
        eigens[n-1] = pc_c_sqrt_two_div_l * y[latest];
        latest = !latest;
    }
}

void ViolinString::finger(const float ratio_from_nut)
{
    const float ratio_from_bridge = 1.0 - ratio_from_nut;
    if (! (almostEquals(vpa_finger_x1, ratio_from_bridge)) ) {
        vpa_finger_x1 = ratio_from_bridge;
        recache_vpa_c = true;

        calculate_eigens(vpa_c_finger_eigens, vpa_finger_x1);
    }
}

void ViolinString::pluck(const float ratio_from_bridge,
                         const float pluck_force)
{
    vpa_pluck_force = pluck_force * PLUCK_FORCE_SCALE;
    m_active = true;
    if (! (almostEquals(vpa_bow_x0, ratio_from_bridge)) ) {
        vpa_bow_x0 = ratio_from_bridge;
        recache_vpa_c = true;

        calculate_eigens(vpa_c_bow_eigens, vpa_bow_x0);
    }
}


void ViolinString::bow(const float bow_ratio_from_bridge,
                       const float bow_force, const float bow_velocity)
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

void ViolinString::set_bow_friction(float mu_s_next, float mu_d_next) {
    mu_s = mu_s_next;
    mu_d = mu_d_next;
}

void ViolinString::cache_pc_c()
{
    pc_c_sqrt_two_div_l = sqrt(2.0 / pc.L);

    const float div_pc_pl = 1.0 / pc.pl;
    const float pi_div_l = M_PI / pc.L;
    // text after eqn (2.5)
    const float I = M_PI * pc.d*pc.d*pc.d*pc.d / 64.0;
    for (int n = 1; n <= MODES; ++n) {
        // text after eqn (2.5)
        const float n_pi_div_L = n*pi_div_l;
        const float w0n = sqrt( (pc.T * div_pc_pl) * n_pi_div_L*n_pi_div_L
                                + ((pc.E * I * div_pc_pl)
                                   * n_pi_div_L*n_pi_div_L
                                   * n_pi_div_L*n_pi_div_L ));

        // text on p. 78
        //const float r_n = pc.B1 + pc.B2*(n-1)*(n-1);
        const float r_n = pc.modes[n-1];

        // Other abbreviations
        const float w_n         = sqrt(w0n*w0n - r_n*r_n);
        const float theta_n     = w_n*dt;
        const float R_n         = exp(-r_n*dt);

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

    float A01 = 0.0;
    float A11 = 0.0;
    for (int n = 1; n <= MODES; ++n) {
        const float phix0 = vpa_c_bow_eigens[n-1];
        const float phix1 = vpa_c_finger_eigens[n-1];
        const float X3n = X3[n-1];
        A01 += phix1 * phix0 * X3n;
        A11 += phix1 * phix1 * X3n;
    }

    // eqn (2.28)
    vpa_c_C11 = -1.0 / A11;  // infinitely stiff spring
    vpa_c_C12 = A01 * vpa_c_C11;

    float B00 = 0.0;
    float B01 = 0.0;
    for (int n = 1; n <= MODES; ++n) {
        const float phix0 = vpa_c_bow_eigens[n-1];
        const float phix1 = vpa_c_finger_eigens[n-1];
        const float Y3n = Y3[n-1];
        B00 += phix0 * phix0 * Y3n;
        B01 += phix0 * phix1 * Y3n;
    }

    vpa_c_C01 = 1.0 / (B00 + B01*vpa_c_C12);
    vpa_c_C02 = -B01*vpa_c_C11*vpa_c_C01;

    recache_vpa_c = false;
}


inline float ViolinString::tick()
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

    const float bridge_force = compute_bridge_force();

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

inline void ViolinString::check_active(float bridge_force)
{
    if (fabs(bridge_force) < SUM_BELOW) {
        bool should_stop = true;
        for (int n = 1; n <= MODES; ++n) {
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

void ViolinString::fill_buffer(float* buffer, const int num_samples)
{
    for (int i=0; i<num_samples; i++) {
        buffer[i] = tick();
    }
}

inline void ViolinString::compute_hist_modes()
{
    for (int n = 1; n <= MODES; ++n) {
        m_a_h[n-1]     = X1[n-1]*m_a[n-1] + X2[n-1]*m_adot[n-1];
        m_adot_h[n-1]  = Y1[n-1]*m_a[n-1] + Y2[n-1]*m_adot[n-1];
    }
}

inline void ViolinString::compute_hist_finger()
{
    m_y1_h = 0.0;
    for (int n = 1; n <= MODES; ++n) {
        m_y1_h += m_a_h[n-1] * vpa_c_finger_eigens[n-1];
    }
}

inline void ViolinString::compute_hist_bow()
{
    m_y0dot_h = 0.0;
    for (int n = 1; n <= MODES; ++n) {
        m_y0dot_h += m_adot_h[n-1] * vpa_c_bow_eigens[n-1];
    }
}

// a pluck is just a bow that disappears once it slips
inline float ViolinString::compute_pluck( )
{
    const float F0 = vpa_c_C01*(PLUCK_VELOCITY - m_y0dot_h) + vpa_c_C02*m_y1_h;
    if ( fabs(F0) > MU_PLUCK*vpa_pluck_force ) {
        vpa_pluck_force = 0.0;
    }
    return F0;
}

inline float ViolinString::compute_bow()
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
        const float F0 = vpa_c_C01*( vpa_bow_velocity - m_y0dot_h)
                         + vpa_c_C02*m_y1_h;
        // text after (2.31)
        if ( fabs(F0) > mu_s*vpa_bow_force ) {
            m_bow_slipping = true;
        }
        return F0;
    } else {
        // is currently slipping

        // add random noise
        const float ut = rand() / (float)RAND_MAX;
        const float N = 1.0 - A_noise * ut;

        float v_c;
        float f_c;
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
        const float div_v_c = 1.0 / v_c;
        const float c2 = -vpa_c_C01*div_v_c;
        const float c1 = (vpa_c_C01*((v_c - vpa_bow_velocity + m_y0dot_h))
                          + mu_d*f_c - vpa_c_C02*m_y1_h) * div_v_c;
        const float c0 = vpa_c_C01*(vpa_bow_velocity - m_y0dot_h)
                         + vpa_c_C02*m_y1_h - mu_s*f_c;
        const float Delta = c1*c1 - 4.0*c0*c2;

        if (Delta < 0.0) {
            // no real solutions for relative bow velocity:
            // bow has stuck to string, so bail out
            m_bow_slipping = false;
            return vpa_c_C01*(vpa_bow_velocity - m_y0dot_h) + vpa_c_C02*m_y1_h;
        } else {
            // bow might still slipping
            const float dv = (-c1 + sqrt(Delta))/(2.0*c2);

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


inline float ViolinString::compute_finger()
{
    if (vpa_finger_x1 != 0.0) {
        return vpa_c_C11 * m_y1_h  +  vpa_c_C12 * m_string_excitation;
    } else {
        return 0.0;
    }
}

inline void ViolinString::apply_forces()
{
    for (int n = 1; n <= MODES; ++n)
    {
        const float position_forces = vpa_c_bow_eigens[n-1]*m_string_excitation +
                                      vpa_c_finger_eigens[n-1]*m_finger_dampening;
        m_a[n-1] = m_a_h[n-1] + X3[n-1] * position_forces;
        m_adot[n-1] = m_adot_h[n-1] + Y3[n-1] * position_forces;
    }
}

inline float ViolinString::compute_bridge_force()
{
    // equation (2.35)
    float result = 0.0;
    for (int n = 1; n <= MODES; ++n) {
        result += m_a[n-1] * pc_c_bridge_forces[n-1];
    }
    return BRIDGE_AMPLIFY*result;
}

inline bool ViolinString::almostEquals(float one, float two)
{
    // maximum absolute error
    if (fabs(one-two) < FLOAT_EQUALITY_ABSOLUTE_ERROR) {
        return true;
    }
    // don't bother with relative error (yet?)
    return false;
}

