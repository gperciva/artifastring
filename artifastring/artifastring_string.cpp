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

#include "artifastring/artifastring_string.h"

#include <math.h>
///#include <stdlib.h> // for rand()
#include <algorithm> // for std::fill

#include <iostream>
//using namespace std;
#include <stdio.h>

#include <emmintrin.h> // for _mm_setcsr

//#define WARN_SKIP

//#define DEBUG_ONLY_SINE_OUTPUT


#define EIGEN_NO_MALLOC
#include <Eigen/LU>

#ifdef RESEARCH
const int MAX_LINE_LENGTH = 2048;
#endif

const float FLOAT_EQUALITY_ABSOLUTE_ERROR = 1e-10f;
const float PI = 3.14159265358979f;


ArtifastringString::ArtifastringString(InstrumentType which_instrument,
                                       int instrument_number, int string_number,
                                       int fs_multiplication_factor)
{
    //
    //_MM_SET_FLUSH_ZERO_MODE(_MM_FLUSH_ZERO_ON);
    //_MM_SET_DENORMALS_ZERO_MODE(_MM_DENORMALS_ZERO_ON);

    // set SSE denormals
    _mm_setcsr( _mm_getcsr() | 0x8040 );

    // do NOT make this time(NULL); we want repeated
    // runs of the program to be identical!
    srand( string_number );

    switch (which_instrument) {
    case Violin: {
        int number = instrument_number % CONSTANTS_VIOLIN_NUM;
        set_physical_constants( violin_params[number][string_number] );
        break;
    }
    case Viola: {
        int number = instrument_number % CONSTANTS_VIOLA_NUM;
        set_physical_constants( viola_params[number][string_number] );
        break;
    }
    case Cello: {
        int number = instrument_number % CONSTANTS_CELLO_NUM;
        set_physical_constants( cello_params[number][string_number] );
        break;
    }
    }
    fs_multiplier = fs_multiplication_factor;

    fs = fs_multiplier * ARTIFASTRING_INSTRUMENT_SAMPLE_RATE;
    dt = 1.0f / fs;
    //printf("fs: %i\tmult: %i\n", fs, fs_multiplier);

#ifdef RESEARCH
    logfile = NULL;
#endif
    debug_string_num = string_number;

    // must happen after opening logfile!
    reset();
    //cache_pc_c();
}

ArtifastringString::~ArtifastringString()
{
#ifdef RESEARCH
    logfile_close();
#endif
}

void ArtifastringString::reset()
{
#ifdef RESEARCH
    time_seconds = 0.0;
    num_skips = 0;
#endif
    // init everything, just to be safe
    cache_pc_c();

    plucks = 0;

    vc.x0  = 0.0f;
    vc.x1  = 0.0f;
    vc.x2  = 0.0f;
    vc.y_pluck = 0.0f;
    vc.y_pluck_target = 0.0f;
    va.Fb  = 0.0f;
    va.vb  = 0.0f;
    va.vb_target = 0.0f;
    va.va = 0.0f;
    vc.pluck_samples_remaining = 0;
    vc.recache = true;

    va.finger_position = 0.0f;
    va.bow_pluck_position = 0.0f;
    va.Kf = K_FINGER;

    vc.K0 = 0.0f;
    vc.R0 = 0.0f;
    vc.K2 = 0.0f;
    vc.K2 = 0.0f;

    ss.actions = OFF;

    ss.a.setZero();
    ss.ad.setZero();
    ss.slipstate = 0;

    debug_ticks = 0;
}

#ifdef RESEARCH
bool ArtifastringString::set_logfile(const char *filename)
{
    logfile_close();
    if (strlen(filename) == 0) {
        return true;
    }

    logfile = fopen(filename, "w");
    if (logfile == NULL) {
        return false;
    }

    char textline[MAX_LINE_LENGTH];
    sprintf(textline, "#time\tm_y0dot_h\tdv\tF0\tslip\tskip_warning\n");
    fwrite(textline, sizeof(char), strlen(textline), logfile);

    // for recache to get init params
    vc.recache = true;

    return true;
}

void ArtifastringString::logfile_data()
{
#ifdef RESEARCH
    if (logfile != NULL) {
        char textline[MAX_LINE_LENGTH];
        sprintf(textline,
                "%g\t%g\t%g\t%g\t%i\t%i\n",
                time_seconds, m_v0h, m_dv, m_F0, ss.slipstate, m_skip);
        fwrite(textline, sizeof(char), strlen(textline), logfile);
        time_seconds += dt;
    }
#endif
}
#endif

#ifdef RESEARCH
void ArtifastringString::logfile_close()
{
    if (logfile != NULL) {
        fclose(logfile);
        logfile = NULL;
    }
}
#endif

void ArtifastringString::finger(const float ratio_from_nut,
                                const float Kf_get)
{
    assert(ratio_from_nut >= 0.0f);
    assert(ratio_from_nut <= 1.0f);

    if (ratio_from_nut == 0.0f) {
        va.finger_position = 0.0f;
    } else {
        va.finger_position = pc.L * (1.0 - ratio_from_nut);
    }

    va.Kf = Kf_get * K_FINGER;
    /*
    if (ratio_from_nut == 0.0) {
        vc.x1 = 0; // yes, don't reverse this one; optimization
        vc.recache = true;
    } else {
        //vc.K1 = K1;
        vc.K1 = 1e4f;
        vc.x1 = pc.L * (1.0 - ratio_from_nut);
        // yes, always recache here
        vc.recache = true;
    }
    */
    vc.recache = true;
}

void ArtifastringString::pluck(const float ratio_from_bridge,
                               const float pull_distance)
{
    assert(ratio_from_bridge > 0.0f);
    assert(ratio_from_bridge < 1.0f);
    va.bow_pluck_position = pc.L * ratio_from_bridge;

    ss.actions = PLUCK;
    vc.pluck_samples_remaining = PLUCK_SECONDS*fs;
    vc.y_pluck = 0.0f;
    vc.y_pluck_target = pull_distance * PLUCK_DISPLACEMENT;
    //printf("pluck target: %.5g\n", vc.y_pluck_target);

    //printf("starting initial deaden part of pluck\n");
    /*
    vc.x0 = va.bow_pluck_position;
    vc.x1 = va.bow_pluck_position + 0.01;
    */
    //vc.K0 = 1e2f;
    //vc.K1 = 1e8f;
    /*
        const float distance_from_bridge = pc.L * ratio_from_bridge;
        if (! (almostEquals(vc.x0, distance_from_bridge)) )
        {
            vc.x0  = distance_from_bridge;
            vc.recache = true;
        }
        */
    vc.recache = true;
}

void ArtifastringString::bow(const float bow_ratio_from_bridge,
                             const float bow_force, const float bow_velocity)
{
    //printf("bow: %g %g %g   tension %g\n", bow_ratio_from_bridge, bow_force, bow_velocity, pc.T);
    if (bow_force == 0) {
        string_release();
        return;
    }
    va.Fb = bow_force;
    va.vb = bow_velocity;
    const float bow_distance_from_bridge = pc.L * bow_ratio_from_bridge;
    if ( !(almostEquals(va.bow_pluck_position, bow_distance_from_bridge))
            || (ss.actions != BOW))
    {
        va.bow_pluck_position = bow_distance_from_bridge;
        //vc.x0 = bow_distance_from_bridge;
        vc.recache = true;
        //printf("recache %i\n", debug_string_num);
    }
    ss.actions = BOW;
}

void ArtifastringString::bow_accel(const float bow_ratio_from_bridge,
                                   const float bow_force, const float bow_velocity_target,
                                   const float bow_accel)
{
    ss.actions = BOW_ACCEL;
    va.Fb = bow_force;
    va.va = bow_accel * dt;
    va.vb_target = bow_velocity_target;
    const float bow_distance_from_bridge = pc.L * bow_ratio_from_bridge;
    if (! (almostEquals(va.bow_pluck_position, bow_distance_from_bridge)) )
    {
        va.bow_pluck_position = bow_distance_from_bridge;
        //vc.x0 = bow_distance_from_bridge;
        vc.recache = true;
    }
}

String_Physical ArtifastringString::get_physical_constants()
{
    String_Physical pc_copy = pc;
    return pc_copy;
}

void ArtifastringString::set_physical_constants(String_Physical pc_new)
{
    pc = pc_new;
    cache_pc_c();
    vc.recache = true;
}

void ArtifastringString::cache_pc_c()
{
    sc.div_pc_L = 1.0f / pc.L;
    sc.sqrt_two_div_L = sqrt( 2.0f / pc.L);
    const float I = PI * pc.d*pc.d*pc.d*pc.d / 64.0f;
    const AA n = AA::LinSpaced(Eigen::Sequential, MODES, 1, MODES);
    const AA w0 = ( (pc.T/pc.pl) * ((n*PI*sc.div_pc_L).square())
                    + (pc.E*I/pc.pl) * ((n*PI*sc.div_pc_L).square().square()) ).sqrt();
    AA r;
    for (int i = 0; i < MODES; ++i) {
        r(i) = pc.rn[i];
    }
    const AA w = (w0.square() - r.square()).sqrt();

    sc.X1 = ((w*dt).cos() + (r/w)*((w*dt).sin())) * ((-r*dt).exp());
    sc.X2 = ((AA::Ones() / w) * (w*dt).sin()) * ((-r*dt).exp());
    sc.X3 = (AA::Ones() - sc.X1) / (pc.pl * w0.square());
    //std::cout<<"X1"<<std::endl<<sc.X1<<std::endl;
    //std::cout<<"X3"<<std::endl<<sc.X3<<std::endl;

    sc.Y1 = -(w + r.square()/w) * (w*dt).sin() * (-r*dt).exp();
    sc.Y2 = ((w*dt).cos() - (r/w)*((w*dt).sin())) * (-r*dt).exp();
    sc.Y3 = -sc.Y1 / (pc.pl * w0.square());

    //std::cout<<"Y3"<<std::endl<<sc.Y3<<std::endl;

    sc.G = sc.sqrt_two_div_L * (pc.T*(n*PI*sc.div_pc_L) + pc.E*I*(n*PI*sc.div_pc_L).cube());

    vc.recache = true;
}

void ArtifastringString::setup_vc_positions()
{
    vc.x1 = va.finger_position;
    vc.K1 = va.Kf;
    vc.R1 = R_FINGER * (va.Kf / K_FINGER);

    switch(ss.actions) {
    case BOW_ACCEL:
    case BOW: {
        vc.x0 = va.bow_pluck_position;
        vc.x2 = 0.0f;
        break;
    }
    case RELEASE: {
        vc.x2 = 0.0f;
        vc.K2 = 0.0f;
        vc.R2 = 0.0f;
        if (va.finger_position == 0 ) {
            vc.x0 = 0.0f;
            vc.K0 = 0.0f;
            vc.R0 = 0.0f;
        } else {
            vc.K0 = vc.K1;
            vc.R0 = vc.R1;
            if (va.finger_position < pc.L - FINGER_WIDTH) {
                vc.x0 = va.finger_position + FINGER_WIDTH;
            } else {
                const float remaining_string = pc.L - va.finger_position;
                vc.x0 = va.finger_position + 0.5f*remaining_string;
            }
        }
        break;
    }
    case PLUCK: {
        vc.x0 = va.bow_pluck_position;
        vc.K0 = K_PLUCK;
        vc.R0 = R_PLUCK;
        vc.x2 = va.bow_pluck_position + PLUCK_WIDTH;
        vc.K2 = K_PLUCK;
        vc.R2 = R_PLUCK;
        break;
    }
    case OFF: {
        return;
        break;
    }
    }
    //printf("setup_vc_positions st %i: x0, x1, x2:\t%.4f\t%.4f\t%.4f\n",
    //       debug_string_num, vc.x0, vc.x1, vc.x2);
}


void ArtifastringString::cache_pa_c()
{
    //printf("cache_pa_c(), string %i, state %i\n",
    //    debug_string_num, ss.actions);


    setup_vc_positions();
    //printf("Ks Rs: %g %g %g %g %g %g\n",
    //    vc.K0, vc.K1, vc.K2, vc.R0, vc.R1, vc.R2
    //    );

    const AA n = AA::LinSpaced(Eigen::Sequential, MODES, 1, MODES);
    const AA inside_phi = n*PI*sc.div_pc_L;
    vc.phix0 = sc.sqrt_two_div_L * ( vc.x0*inside_phi ).sin();
    vc.phix1 = sc.sqrt_two_div_L * ( vc.x1*inside_phi ).sin();

    const float A00 = (sc.X3 * vc.phix0 * vc.phix0).sum();
    const float A01 = (sc.X3 * vc.phix0 * vc.phix1).sum();
    const float A11 = (sc.X3 * vc.phix1 * vc.phix1).sum();

    const float B00 = (sc.Y3 * vc.phix0 * vc.phix0).sum();
    const float B01 = (sc.Y3 * vc.phix0 * vc.phix1).sum();
    const float B11 = (sc.Y3 * vc.phix1 * vc.phix1).sum();

    switch(ss.actions) {
    case BOW_ACCEL:
    case BOW: {
        /*
        const float L2 = 1.0f / (A11*B00*vc.K1 - A01*B01*vc.K1+B00);
        vc.D5 = (1.0f + vc.K1*A11) * L2;
        vc.D6 = B01*vc.K1*L2;
        vc.D7 = 1.0f / (2.0f * vc.D5);
        */

        // bow coefficients
        const float L1 = 1.0f / (
                             (B00*B11 - B01*B01)*vc.R1 + (A11*B00 - A01*B01)*vc.K1 + B00);
        //printf("L1 parts: %g %g %g\n",
        //    (B00*B11 - B01*B01)*vc.R1, (A11*B00 - A01*B01)*vc.K1, B00);
        vc.D1 = (B11*vc.R1 + A11*vc.K1 + 1.0f)*L1;
        vc.D4 = 0.5f / vc.D1;
        vc.D2 = B01 * vc.K1 * L1;
        vc.D3 = B01 * vc.R1 * L1;

        // finger-during-bowing coefficients
        const float L2 = -1.0f / (B11*vc.R1 + A11*vc.K1 + 1.0f);
        vc.D5 = (B01*vc.R1 + A01*vc.K1) * L2;
        vc.D6 = vc.R1 * L2;
        vc.D7 = vc.K1 * L2;

        /*
                printf("D1: %g\n", vc.D1);
                printf("mu_s: %g\n", pc.mu_s);
                printf("mu_d: %g\n", pc.mu_d);
                printf("mu_v0: %g\n", pc.v0);
                */

        /*
                printf("L1, D1, D2, D3, D4\n");
                printf("%g %g %g %g %g\n", L1, vc.D1, vc.D2, vc.D3, vc.D4);
                printf("L2, D5, D6, D7\n");
                printf("%g %g %g %g\n", L2, vc.D5, vc.D6, vc.D7);
        */
        break;
    }
    case PLUCK: {
        vc.phix2 = sc.sqrt_two_div_L * ( vc.x2*inside_phi ).sin();
        const float A02 = (sc.X3 * vc.phix0 * vc.phix2).sum();
        const float A12 = (sc.X3 * vc.phix1 * vc.phix2).sum();
        const float A22 = (sc.X3 * vc.phix2 * vc.phix2).sum();

        const float B02 = (sc.Y3 * vc.phix0 * vc.phix2).sum();
        const float B12 = (sc.Y3 * vc.phix1 * vc.phix2).sum();
        const float B22 = (sc.Y3 * vc.phix2 * vc.phix2).sum();

        Eigen::Matrix3f matrix_A;
        matrix_A <<
                 B00*vc.R0 + A00*vc.K0 + 1.0f, B01*vc.R0 + A01*vc.K0,        B02*vc.R0 + A02*vc.K0,
                     B01*vc.R1 + A01*vc.K1,        B11*vc.R1 + A11*vc.K1 + 1.0f, B12*vc.R1 + A12*vc.K1,
                     B02*vc.R2 + A02*vc.K2,        B12*vc.R2 + A12*vc.K2,        B22*vc.R2 + A22*vc.K2 + 1.0f;
        //qr.compute(
        //    matrix_A);

        inv_A = matrix_A.inverse();

        /*
                Eigen::Matrix2f matrix_A_release;
                matrix_A_release <<
                                 B11*vc.R1 + A11*vc.K1 + 1.0f, B12*vc.R1 + A12*vc.K1,
                                     B12*vc.R2 + A12*vc.K2,        B22*vc.R2 + A22*vc.K2 + 1.0f;
                qr2.compute(
                    matrix_A_release);
                inv_A_release = matrix_A_release.inverse();
                */
        //printf("inverse\n");
        //std::cout<< inv_A_release << std::endl;
        /*
          (Eigen::MatrixXf(3,3) << B00*vc.R0 + A00*vc.K0 + 1.0f, B01*vc.R0 + A01*vc.K0,        B02*vc.R0 + A02*vc.K0,
          B01*vc.R1 + A01*vc.K1,        B11*vc.R1 + A11*vc.K1 + 1.0f, B12*vc.R1 + A12*vc.K1,
          B02*vc.R2 + A02*vc.K2,        B12*vc.R2 + A12*vc.K2,        B22*vc.R2 + A22*vc.K2 + 1.0f).finished()
            );

        std::cout<< (Eigen::Matrix2f << 0, 1, 1, 0).finished();
        std::cout<<std::endl;
            */

        //std::cout<<A<<std::endl;
        break;
    }
    case RELEASE: {
        const float M00 = A00*vc.K1 + B00*vc.R1 + 1.0f;
        const float M01 = A01*vc.K1 + B01*vc.R1;
        const float M11 = A11*vc.K1 + B11*vc.R1 + 1.0f;

        const float L3 = -1.0f / ( M00 * M11 - M01*M01 );
        vc.D8 = -1.0 / M00;
        vc.D9 = M01 * vc.D8;
        vc.D10 = -M01 * L3;
        vc.D11 = M00 * L3;

        // extra inv_A for any remaining tick_pluck() which
        // occurs before a new buffer is called
        // (i.e. the switch/case in fill_buffer)
        Eigen::Matrix3f matrix_A;
        matrix_A <<
                 B00*vc.R0 + A00*vc.K0 + 1.0f, B01*vc.R0 + A01*vc.K0, 0.0f,
                     B01*vc.R1 + A01*vc.K1,        B11*vc.R1 + A11*vc.K1 + 1.0f, 0.0f,
                     0.0f, 0.0f, 1.0f;
        //qr.compute(
        //    matrix_A);

        inv_A = matrix_A.inverse();

        break;
    }
    case OFF: {
        break;
    }
    }

    /*
        const float L1old = -vc.K0 / (A00*A11*vc.K0*vc.K1
                                         - A01*A10*vc.K0*vc.K1
                                         + A11*vc.K1 + A00*vc.K0 + 1.0f);
        vc.D1old = -vc.K1 / (1.0f + vc.K1*A11);
        vc.D2old = A10 * vc.D1old;
        vc.D3old = (1.0f + vc.K1*A11) * L1old;
        vc.D4old = -A01*vc.K1*L1old;
    */
    /*
        if (B00 == 0.0f) {
            vc.D5 = 0.0f;
            vc.D6 = 0.0f;
            vc.D7 = 0.0f;
        } else {
            const float L2 = 1.0f / (A11*B00*vc.K1 - A10*B01*vc.K1+B00);
            vc.D5 = (1.0f + vc.K1*A11) * L2;
            vc.D6 = B01*vc.K1*L2;
            vc.D7 = 1.0f / (2.0f * vc.D5);
        }
    */
    //printf("Ds: %g %g %g %g %g %g\n", vc.D1old, vc.D2old, vc.D3old, vc.D4old, vc.D5, vc.D6);
    vc.recache = false;
}


inline float ArtifastringString::tick_bow()
{
    // "hands-free" modes
    const AA ah  = sc.X1*ss.a + sc.X2*ss.ad;
    const AA adh = sc.Y1*ss.a + sc.Y2*ss.ad;

    const float y1h = (vc.x1 > 0) ? (vc.phix1 * ah).sum() : 0;
    const float v1h = (vc.x1 > 0) ? (vc.phix1 * adh).sum() : 0;
    //const float y1h = (vc.phix1 * ah).sum();
    //const float v1h = (vc.phix1 * adh).sum();
    // Calculate excitation force
    const float v0h = (vc.phix0 * adh).sum();

    const float F0 = compute_bow(v0h, y1h, v1h);
    const float F1 = vc.D5*F0 + vc.D6*v1h + vc.D7*y1h;
    /*
    if (debug_string_num == 0) {
        //printf("%f %f %f\n", y1h, v1h, v0h);
        //printf("F0, F1\t%g %g\n", F0, F1);
        printf("%g\n", F0);
    }
    */

    {   // apply forces
        const AA fn = vc.phix0*F0 + vc.phix1*F1;
        //std::cout<<fn<<std::endl;
        ss.a  = ah  + sc.X3*fn;
        ss.ad = adh + sc.Y3*fn;
    }

#ifdef RESEARCH
    m_F0 = F0;
    m_v0h = v0h;
#endif
    tick_output_force = F0;
    return compute_bridge_force();
}

inline float ArtifastringString::tick_pluck()
{
    // "hands-free" modes
    const AA ah  = sc.X1*ss.a + sc.X2*ss.ad;
    const AA adh = sc.Y1*ss.a + sc.Y2*ss.ad;

    // "hands-free" string displacement under force locations
#if 1
    const float y0h = (vc.phix0 * ah).sum();
    const float y1h = (vc.phix1 * ah).sum();
    const float y2h = (vc.phix2 * ah).sum();
    const float v0h = (vc.phix0 * adh).sum();
    const float v1h = (vc.phix1 * adh).sum();
    const float v2h = (vc.phix2 * adh).sum();
    const Eigen::Vector3f matrix_b =
        (Eigen::Vector3f() <<
         -v0h * vc.R0 - (y0h-vc.y_pluck) * vc.K0,
         -v1h * vc.R1 - y1h * vc.K1,
         -v2h * vc.R2 - (y2h-vc.y_pluck) * vc.K2
        ).finished();
#else
    const Eigen::Matrix<float, MODES, 3> vcs =
        (Eigen::Matrix<float, MODES, 3>()
         << vc.phix0, vc.phix1, vc.phix2).finished();

    const Eigen::Matrix<float, 2, MODES> ahs =
        (Eigen::Matrix<float, 2, MODES>()
         << ah.transpose(), adh.transpose()).finished();

    const Eigen::Matrix<float, Eigen::Dynamic, Eigen::Dynamic> yv = ahs * vcs;

    /*
        std::cout<< yv.rows() << "\t" << yv.cols() << std::endl;
        printf("%g %g %g\n", y0h, y1h, y2h);
        printf("%g %g %g\n", yv(0,0), yv(0,1), yv(0,2));
        //std::cout<< yv <<std::endl;
        printf("\n");
        */

    const Eigen::Vector3f matrix_b =
        (Eigen::Vector3f() <<
         -yv(1,0) * vc.R0 - (yv(0,0)-vc.y_pluck) * vc.K0,
         -yv(1,1) * vc.R1 - yv(0,1) * vc.K1,
         -yv(1,2) * vc.R2 - (yv(0,2)-vc.y_pluck) * vc.K2
        ).finished();
#endif
    // forces at those locations

    const Eigen::Vector3f Fs = inv_A * matrix_b;

    // apply forces
    const AA fn = vc.phix0*Fs(0) + vc.phix1*Fs(1) + vc.phix2*Fs(2);
    ss.a  = ah  + sc.X3*fn;
    ss.ad = adh + sc.Y3*fn;
    return compute_bridge_force();
}

inline float ArtifastringString::tick_release()
{
    // "hands-free" modes
    const AA ah  = sc.X1*ss.a + sc.X2*ss.ad;
    const AA adh = sc.Y1*ss.a + sc.Y2*ss.ad;

    // "hands-free" string displacement under force locations
    const float y0h = (vc.phix0 * ah).sum();
    const float y1h = (vc.phix1 * ah).sum();
    //const float y2h = (vc.phix2 * ah).sum();
    const float v0h = (vc.phix0 * adh).sum();
    const float v1h = (vc.phix1 * adh).sum();
    //const float v2h = (vc.phix2 * adh).sum();
    /*
    const float y1h = ah.matrix().dot(vc.phix1.matrix());
    const float y2h = ah.matrix().dot(vc.phix2.matrix());
    const float v1h = adh.matrix().dot(vc.phix1.matrix());
    const float v2h = adh.matrix().dot(vc.phix2.matrix());
    */
    /*
    printf("y1h, y2h, v1h, v2h:\t%g %g %g %g\n",
        y1h, y2h, v1h, v2h);
    */

    /*
        Eigen::Vector3f matrix_b;
        matrix_b << -v0h * vc.R0 - (y0h-vc.y_pluck) * vc.K0,
                 -v1h * vc.R1 - y1h * vc.K1,
                 -v2h * vc.R2 - (y2h-vc.y_pluck) * vc.K2;
        */
    /*
    matrix_b <<
             -v1h * vc.R1 - y1h * vc.K1,
             -v2h * vc.R2 - y2h * vc.K2;
      */
    //matrix_b << 0, 0;
    //printf("matrix_b:\n");
    //std::cout<<matrix_b<<std::endl;

    //(void) inv_A;
    //(void) b;
    //std::cout<<b;
    //const Eigen::Vector2f Fs = qr2.solve(matrix_b);
    //const Eigen::Vector2f Fs = inv_A_release * matrix_b;
    //const Eigen::Vector3f Fs = inv_A * matrix_b;
    //Eigen::Vector3f Fs;
    //Fs << 0, 0, 0;

    /*
    debug_ticks++;
    std::cout<<debug_ticks<<std::endl;

    std::cout<< "---" <<std::endl;
    std::cout<< vc.y_pluck <<std::endl;
    std::cout<< b <<std::endl;
    std::cout<< Fs <<std::endl;
    */
    // external forces
    //const float F0 = vc.D3old*(y0h-vc.y0d) + vc.D4old*y1h;
    //const float F1 = vc.D1old*y1h          + vc.D2old*F0;

    const float ans0 = vc.K1*y0h + vc.R1*v0h;
    const float ans1 = vc.K1*y1h + vc.R1*v1h;

    const float F1 = ans0 * vc.D10 + ans1 * vc.D11;
    const float F0 = ans0 * vc.D8 + F1 * vc.D9;

    // apply forces
    {
        //const AA fn = vc.phix0*Fs(0) + vc.phix1*Fs(1);
        //const AA fn = vc.phix0*Fs(0) + vc.phix1*Fs(1) + vc.phix2*Fs(2);
        const AA fn = vc.phix0*F0 + vc.phix1*F1;
        //std::cout<<fn<<std::endl;
        ss.a  = ah  + sc.X3*fn;
        ss.ad = adh + sc.Y3*fn;
    }
    return compute_bridge_force();
}

inline float ArtifastringString::tick_free()
{
    // necessary to avoid aliasing
    const AA ah  = sc.X1*ss.a + sc.X2*ss.ad;
    const AA adh = sc.Y1*ss.a + sc.Y2*ss.ad;
    ss.a  = ah;
    ss.ad = adh;
    return compute_bridge_force();
}


void ArtifastringString::update_bow_accel() {
    // accelerate bow
    va.vb += va.va;
    if (va.va > 0) {
        if (va.vb > va.vb_target) {
            va.vb = va.vb_target;
            ss.actions = BOW;
        }
    } else {
        if (va.vb < va.vb_target) {
            va.vb = va.vb_target;
            ss.actions = BOW;
        }
    }
    //printf("%g\t%g\n", time_seconds, va.vb);
    //printf("%g\n", va.vb);
}

void ArtifastringString::update_pluck_actions() {
    vc.pluck_samples_remaining -= 1;
    if (vc.y_pluck < vc.y_pluck_target) {
        vc.y_pluck += PLUCK_VELOCITY*dt;
    }
    //printf("%i\t%.4f\n", vc.pluck_samples_remaining, vc.y0d);
    //vc.y0d += std::min(PLUCK_ACCELERATION, PLUCK_DISPLACEMENT - vc.y0d);
    if (vc.pluck_samples_remaining == 0) {
        // pluck stop
        string_release();
    }
}

void ArtifastringString::string_release() {
    //printf("release num %i\n", debug_string_num);
    ss.actions = RELEASE;
    vc.y_pluck = 0;
    // can't use lazy evaluation this time,
    // because we aren't guaranteed to end fill_buffer()
    // on a 1024-sample boundary!
    cache_pa_c();
}

void ArtifastringString::fill_buffer_forces(float *buffer, float *forces,
        const int num_samples_instrument)
{
    if (vc.recache) {
        cache_pa_c();
    }
    int num_samples = fs_multiplier * num_samples_instrument;
    //printf("# fill_buffer_forces()  string_num, ss.actions, ticks, num_samples_instrument, num_samples\n: %i %i %i %i %i\n",
    //    debug_string_num, ss.actions, debug_ticks, num_samples_instrument, num_samples);

#ifdef DEBUG_ONLY_SINE_OUTPUT
    if (va.Fb == 0) {
        for (int i=0; i<num_samples; i++) {
            buffer[i] = 0;
            if (forces != NULL) {
                forces[i] = 0;
            }
        }
        return;
    }
    for (int i=0; i<num_samples; i++) {
        buffer[i] = sin( 10000.0*2*M_PI*dt*debug_ticks);
        //printf("%g\n", buffer[i]);
        if (forces != NULL) {
            forces[i] = sin( 10000.0*2*M_PI*dt*debug_ticks);
        }
        debug_ticks++;
    }
    return;
#endif



    switch(ss.actions) {
    case BOW: {
        //assert(force_samples != NULL);
        if (forces != NULL) {
            for (int i=0; i<num_samples; i++)
            {
                buffer[i] = tick_bow();
                forces[i] = tick_output_force;
                //printf("%g\n", tick_output_force);
#ifdef RESEARCH
                logfile_data();
#endif
            }
        } else {
            for (int i=0; i<num_samples; i++)
            {
                buffer[i] = tick_bow();
            }
        }
        /*
        for (int i=0; i<num_samples; i++)
        {
            buffer[i] = audio_samples[i];
        }
        */

        break;
    }
    case BOW_ACCEL: {
        //assert(force_samples != NULL);
        if (forces != NULL) {
            for (int i=0; i<num_samples; i++)
            {
                buffer[i] = tick_bow();
                forces[i] = tick_output_force;
                update_bow_accel();
#ifdef RESEARCH
                logfile_data();
#endif
            }
        } else {
            for (int i=0; i<num_samples; i++)
            {
                buffer[i] = tick_bow();
                update_bow_accel();
            }
        }
        break;
    }
    case RELEASE: {
        if (va.finger_position == 0) {
            for (int i=0; i<num_samples; i++)
            {
                buffer[i] = tick_free();
                //debug_ticks++;
#ifdef RESEARCH
                logfile_data();
#endif
            }
        } else {
            for (int i=0; i<num_samples; i++)
            {
                buffer[i] = tick_release();
                //debug_ticks++;
#ifdef RESEARCH
                logfile_data();
#endif
            }
        }
        //if (force_samples != NULL) {
        //std::fill(force_samples, force_samples+num_samples, 0.0);
        //}
        // check if we should turn off the string
        // TODO: only check if num_samples >= large enough
        // audio_samples size
        if (num_samples == fs_multiplier*NORMAL_BUFFER_SIZE) {
            float sum_squared = 0.0;
            for (int i=0; i<num_samples; i++)
            {
                sum_squared += buffer[i]*buffer[i];
            }
            if (sum_squared < pc.cutoff) {
                ss.actions = OFF;
                //printf("string turned off\n");
            }
        }
        break;
    }
    case PLUCK: {
        for (int i=0; i<num_samples; i++)
        {
            buffer[i] = tick_pluck();
            //debug_ticks++;
            if (vc.pluck_samples_remaining > 0) {
                update_pluck_actions();
            }
            // if the pluck runs out, we'll still be calling
            // tick_pluck() but that's ok because the formula is
            // sufficiently general to handle that case as long as
            // x2 = 0
#ifdef RESEARCH
            logfile_data();
#endif
        }
        //if (force_samples != NULL) {
        //std::fill(force_samples, force_samples+num_samples, 0.0);
        //}
        break;
    }
    case OFF: {
        std::fill(buffer, buffer+num_samples_instrument, 0.0);
        //if (force_samples != NULL) {
        //std::fill(force_samples, force_samples+num_samples, 0.0);
        //}

#ifdef RESEARCH
        for (int i=0; i<num_samples; i++)
        {
            logfile_data();
        }
#endif
        break;
    }
    }
    //zz
}

inline float ArtifastringString::compute_bow_force(
    const float v0h, const float y1h, const float v1h, const float dv)
{
    return vc.D1*(va.vb + dv - v0h) + vc.D2*y1h + vc.D3*v1h;
}
inline float ArtifastringString::compute_bow_slip_negative(
    const float v0h, const float y1h, const float v1h)
{
    // add random noise
    const float ut = rand() / (float)RAND_MAX;
    const float N = 1.0f - A_noise * ut;
    const float ve0 = N*pc.v0; // "v hat 0", or "v estimate 0"

    // handle negative side of friction curve
    const float c1 = -vc.D1*( va.vb - v0h - ve0)
                     -vc.D2*y1h
                     - vc.D3*v1h
                     + va.Fb*pc.mu_d;
    const float c0 = ve0 * (vc.D1 * (va.vb - v0h)
                            + vc.D2*y1h
                            + vc.D3*v1h
                            - va.Fb * pc.mu_s);
    // a real solution exists
    const float Delta = c1*c1 + 4.0f*c0*vc.D1;
    if (Delta >= 0.0f)
    {
        return vc.D4 * (c1 - sqrt(Delta));
    } else {
        return 0.0f;
    }
}

inline float ArtifastringString::compute_bow_slip_positive(
    const float v0h, const float y1h, const float v1h)
{
    // add random noise
    const float ut = rand() / (float)RAND_MAX;
    const float N = 1.0f - A_noise * ut;
    const float ve0 = N*pc.v0; // "v hat 0", or "v estimate 0"

    // handle negative side of friction curve
    const float c1 = vc.D1*( va.vb - v0h + ve0)
                     + vc.D2*y1h + vc.D3*v1h + va.Fb*pc.mu_d;
    const float c0 = ve0 * (vc.D1 * (va.vb - v0h) + vc.D2 * y1h
                            + vc.D3 * v1h + va.Fb * pc.mu_s);
    // a real solution exists
    const float Delta = c1*c1 - 4.0f*c0*vc.D1;
    if (Delta >= 0.0f)
    {
        return vc.D4 * (-c1 + sqrt(Delta));
    } else {
        return 0.0f;
    }
}



inline float ArtifastringString::compute_bow(
    const float v0h, const float y1h, const float v1h)
{
    // GIVEN: bow force is above zero
    float F0;
    float dv;
    //printf("------ slipstate %i\n", ss.slipstate);
#ifdef RESEARCH
    m_dv = 99999;
    m_skip = 0;
#endif
    const float max_stable = pc.mu_s * va.Fb;

    if (ss.slipstate == 0)
    {
        // is sticking
        F0 = compute_bow_force(v0h, y1h, v1h, 0);
        if (abs_le(F0, max_stable))
        {
#ifdef RESEARCH
            m_dv = 0;
#endif
            return F0;
        }
        if (v0h > va.vb)
        {
            dv = compute_bow_slip_positive(v0h, y1h, v1h);
            if (dv > 0)
            {
#ifdef RESEARCH
                m_dv = dv;
#endif
                F0 = compute_bow_force(v0h, y1h, v1h, dv);
                ss.slipstate = 1;
                return F0;
            }
            dv = compute_bow_slip_negative(v0h, y1h, v1h);
            if (dv < 0)
            {
#ifdef RESEARCH
                m_dv = dv;
#endif
                F0 = compute_bow_force(v0h, y1h, v1h, dv);
                ss.slipstate = -1;
                return F0;
            }
            printf("yikes bad stick->positive\n");
        }
        else
        {
            dv = compute_bow_slip_negative(v0h, y1h, v1h);
            if (dv < 0)
            {
#ifdef RESEARCH
                m_dv = dv;
#endif
                F0 = compute_bow_force(v0h, y1h, v1h, dv);
                ss.slipstate = -1;
                return F0;
            }
            dv = compute_bow_slip_positive(v0h, y1h, v1h);
            if (dv > 0)
            {
#ifdef RESEARCH
                m_dv = dv;
#endif
                F0 = compute_bow_force(v0h, y1h, v1h, dv);
                ss.slipstate = 1;
                return F0;
            }
            printf("yikes bad stick->negative\n");
        }
    }
    if (ss.slipstate == -1)
    {
        // is slipping
        dv = compute_bow_slip_negative(v0h, y1h, v1h);
        if (dv < 0)
        {
#ifdef RESEARCH
            m_dv = dv;
#endif
            F0 = compute_bow_force(v0h, y1h, v1h, dv);
            return F0;
        }
        F0 = compute_bow_force(v0h, y1h, v1h, 0);
        if (abs_le(F0, max_stable))
        {
#ifdef RESEARCH
            m_dv = 0;
#endif
            ss.slipstate = 0;
            return F0;
        }
        else
        {
            dv = compute_bow_slip_positive(v0h, y1h, v1h);
            if (dv > 0)
            {
#ifdef RESEARCH
                m_skip = 1;
                num_skips++;
                m_dv = dv;
#endif
#ifdef WARN_SKIP
                printf("# bow skip negative->positive, st %i\n", debug_string_num);
#endif
                F0 = compute_bow_force(v0h, y1h, v1h, dv);
                num_friction_skip_over_stick++;
                ss.slipstate = 1;
                return F0;
            }
            printf("# yikes impossible failed -1\n");
            return 0;
        }
    }
    if (ss.slipstate == 1)
    {
        // is slipping
        dv = compute_bow_slip_positive(v0h, y1h, v1h);
        if (dv > 0)
        {
#ifdef RESEARCH
            m_dv = dv;
#endif
            F0 = compute_bow_force(v0h, y1h, v1h, dv);
            return F0;
        }
        F0 = compute_bow_force(v0h, y1h, v1h, 0);
        if (abs_le(F0, max_stable))
        {
#ifdef RESEARCH
            m_dv = dv;
#endif
            ss.slipstate = 0;
            return F0;
        }
        else
        {
            dv = compute_bow_slip_negative(v0h, y1h, v1h);
            if (dv < 0)
            {
#ifdef RESEARCH
                m_skip = 1;
                num_skips++;
                m_dv = dv;
#endif
#ifdef WARN_SKIP
                printf("# bow skip positive->negative, st %i\n", debug_string_num);
#endif
                F0 = compute_bow_force(v0h, y1h, v1h, dv);
                num_friction_skip_over_stick++;
                ss.slipstate = -1;
                return F0;
            }
            printf("# yikes impossible failed 1\n");
            return 0;
        }
    }
    printf("# yikes impossible failed everything\n");
    printf("slipstate: %i\n", ss.slipstate);
    printf("v0h: %g\n", v0h);
    return 0;
}



inline float ArtifastringString::compute_bridge_force()
{
    return (ss.a * sc.G).sum();
}

inline bool ArtifastringString::abs_le(const float one, const float two)
{
    if ( (fabsf(one) - two) <= std::numeric_limits<float>::epsilon()) {
        return true;
    } else {
        return false;
    }
}

inline bool ArtifastringString::almostEquals(float one, float two)
{
    // maximum absolute error
    if (fabs(one-two) < FLOAT_EQUALITY_ABSOLUTE_ERROR)
    {
        return true;
    }
    // don't bother with relative error (yet?)
    return false;
}

