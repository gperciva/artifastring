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
 *
 */

#include <limits.h>
#include <cstddef>

#include <algorithm>

extern "C" {
#include <complex.h>
#include <fftw3.h>
};

#include "artifastring/violin_instrument.h"
//#include "artifastring/violin_constants.h"
#include "artifastring/violin_string.h"

ViolinInstrument::ViolinInstrument(int instrument_number) {
    InstrumentType distinct_instrument;
    switch (instrument_number) {
    case 4:
        distinct_instrument = Viola;
        break;
    case 5:
        distinct_instrument = Cello;
        break;
    default:
        distinct_instrument = Violin;
    }
    for (int st=0; st < NUM_VIOLIN_STRINGS; st++) {
        violinString[st] = new ViolinString(distinct_instrument, st);
    }
    m_bridge_force_amplify = BRIDGE_FORCE_AMPLIFY[distinct_instrument]
                             * SHRT_MAX / CONVOLUTION_SIZE;
    m_bow_force_amplify = BOW_FORCE_AMPLIFY[distinct_instrument]
                          * SHRT_MAX;

    std::fill(f_hole, f_hole+F_HOLE_SIZE, 0.0);
    f_hole_read_index = 0;

    bow_string = 0;

    // setup FFT(kernel)
    float pc_kernel[CONVOLUTION_SIZE] = {0};
    // copy good data
    for (int i = 0; i<PC_KERNEL_SIZE; i++) {
        pc_kernel[i] = pc_kernels[instrument_number][i];
    }
    // FFT stuff
    int kernel_M = (CONVOLUTION_SIZE / 2) + 1;
    body_M = (CONVOLUTION_SIZE / 2) + 1;
    body_in = new float[CONVOLUTION_SIZE];
    body_out = new float[CONVOLUTION_SIZE];

    // critical section --------------
    fftwf_mutex.lock();
    // kernel
    kernel_interim = fftwf_malloc(sizeof(fftwf_complex) * kernel_M);
    fftwf_plan kernel_plan_f = fftwf_plan_dft_r2c_1d(
                                   CONVOLUTION_SIZE,
                                   pc_kernel,
                                   (fftwf_complex*) kernel_interim,
                                   FFTW_ESTIMATE);
    fftwf_execute(kernel_plan_f);
    fftwf_destroy_plan(kernel_plan_f);

    // setup body convolution
    body_interim = fftwf_malloc(sizeof(fftwf_complex) * body_M);


    fftwf_plan body_plan_f = fftwf_plan_dft_r2c_1d(
                                 CONVOLUTION_SIZE,
                                 body_in,
                                 (fftwf_complex*)body_interim,
                                 FFTW_ESTIMATE);
    fftwf_plan body_plan_b = fftwf_plan_dft_c2r_1d(
                                 CONVOLUTION_SIZE,
                                 (fftwf_complex*) body_interim,
                                 body_out,
                                 FFTW_ESTIMATE);
    //fftwf_export_wisdom_to_filename("artifastring.wisdom");

    body_plan_f_p = (fftwf_plan*) body_plan_f;
    body_plan_b_p = (fftwf_plan*) body_plan_b;

    fftwf_mutex.unlock();
    // ------------- critical section end
}

ViolinInstrument::~ViolinInstrument() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        delete violinString[st];
    }
    // critical section --------------
    fftwf_mutex.lock();
    fftwf_destroy_plan((fftwf_plan)body_plan_f_p);
    fftwf_destroy_plan((fftwf_plan)body_plan_b_p);

    fftwf_free(kernel_interim);
    fftwf_free(body_interim);
    fftwf_cleanup();
    fftwf_mutex.unlock();
    // ------------- critical section end
    delete [] body_in;
    delete [] body_out;
}

void ViolinInstrument::reset() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        violinString[st]->reset();
    }
    std::fill(f_hole, f_hole+F_HOLE_SIZE, 0.0);
}

void ViolinInstrument::finger(int which_string, float ratio_from_nut)
{
    violinString[which_string]->finger(ratio_from_nut);
}

void ViolinInstrument::pluck(int which_string, float ratio_from_bridge,
                             float pluck_force)
{
    violinString[which_string]->pluck(ratio_from_bridge, pluck_force);
}

void ViolinInstrument::bow(int which_string, float bow_ratio_from_bridge,
                           float bow_force, float bow_velocity)
{
    bow_string = which_string;
    violinString[which_string]->bow(bow_ratio_from_bridge,
                                    bow_force, bow_velocity);
}

String_Physical ViolinInstrument::get_physical_constants(int which_string)
{
    return violinString[which_string]->get_physical_constants();
}

void ViolinInstrument::set_physical_constants(int which_string,
        String_Physical pc_new)
{
    violinString[which_string]->set_physical_constants(pc_new);
}


void ViolinInstrument::body_impulse()
{
    fftwf_execute((fftwf_plan)body_plan_f_p);
    // pointwise multiplication
    for (int i=0; i<body_M; i++) {
        ((fftwf_complex*)(body_interim))[i] =
            ((fftwf_complex*) body_interim)[i]
            * ((fftwf_complex*) kernel_interim)[i];
    }
    fftwf_execute((fftwf_plan)body_plan_b_p);

    // get output
    int f_hole_write_index = f_hole_read_index;
    for (int i=0; i<CONVOLUTION_ACTUAL_DATA_SIZE; i++) {
        // body_out is un-normalized, but we take care of this
        // with m_bow_force_amplify
        f_hole[f_hole_write_index] += body_out[i];
        // update pointer
        f_hole_write_index++;
        f_hole_write_index &= F_HOLE_SIZE - 1;
    }
}

void ViolinInstrument::wait_samples(short *buffer, int num_samples)
{
    int remaining = num_samples;
    int position = 0;
    while (remaining > NORMAL_BUFFER_SIZE) {
        if (buffer == NULL) {
            handle_buffer(NULL, NULL, NORMAL_BUFFER_SIZE);
        } else {
            handle_buffer(buffer+position, NULL, NORMAL_BUFFER_SIZE);
        }
        remaining -= NORMAL_BUFFER_SIZE;
        position += NORMAL_BUFFER_SIZE;
    }
    if (remaining > 0) {
        handle_buffer(buffer+position, NULL, remaining);
    }
}

void ViolinInstrument::wait_samples_forces(short *buffer, short *forces,
        int num_samples)
{
    int remaining = num_samples;
    int position = 0;
    while (remaining > NORMAL_BUFFER_SIZE) {
        if (buffer == NULL) {
            handle_buffer(NULL, NULL, NORMAL_BUFFER_SIZE); // special case
        } else {
            handle_buffer(buffer+position, forces+position,
                          NORMAL_BUFFER_SIZE);
        }
        remaining -= NORMAL_BUFFER_SIZE;
        position += NORMAL_BUFFER_SIZE;
    }
    if (remaining > 0) {
        handle_buffer(buffer+position, forces+position, remaining);
    }
}


void ViolinInstrument::handle_buffer(short output[], short forces[],
                                     int num_samples)
{
    // calculate string buffers
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        if ((st == bow_string) && (forces != NULL)) {
            violinString[st]->fill_buffer_forces(
                violin_string_buffer[st],
                bow_string_forces,
                num_samples);
        } else {
            violinString[st]->fill_buffer(violin_string_buffer[st],
                                          num_samples);
        }
    }

    // calculate body input from strings
    std::fill(body_in, body_in + CONVOLUTION_SIZE, 0.0);
    for (int i=0; i<num_samples; i++) {
        for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
            body_in[i] += violin_string_buffer[st][i];
        }
    }

    // calculates f_hole output
    body_impulse();

    // get output and forces
    if (output != NULL) {
        for (int i=0; i<num_samples; i++) {
            output[i] = f_hole[f_hole_read_index] * m_bridge_force_amplify;
            f_hole[f_hole_read_index] = 0;
            f_hole_read_index++;
            f_hole_read_index &= F_HOLE_SIZE - 1;
        }
    }
    if (forces != NULL) {
        for (int i=0; i<num_samples; i++) {
            forces[i] = bow_string_forces[i] * m_bow_force_amplify;
        }
    }
}

