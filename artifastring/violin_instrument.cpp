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

#include "artifastring/violin_instrument.h"
#include "artifastring/violin_constants.h"
#include <limits.h>
#include <cstddef>

ViolinInstrument::ViolinInstrument(int random_seed) {
    violinString[3] = new ViolinString(vl_E, NUM_VIOLIN_STRINGS*random_seed+0);
    violinString[2] = new ViolinString(vl_A, NUM_VIOLIN_STRINGS*random_seed+1);
    violinString[1] = new ViolinString(vl_D, NUM_VIOLIN_STRINGS*random_seed+2);
    violinString[0] = new ViolinString(vl_G, NUM_VIOLIN_STRINGS*random_seed+3);

    for (int i = 0; i<BRIDGE_BUFFER_SIZE; i++) {
        bridge_buffer[i] = 0.0;
    }
    // before you doubt this, draw a ring buffer diagram
    bridge_write_index = 0;
#ifdef NO_CONVOLUTION
    bridge_read_index = 0;
#else
    bridge_read_index = BRIDGE_BUFFER_SIZE-PC_KERNEL_SIZE+1;
#endif

}

ViolinInstrument::~ViolinInstrument() {
    delete violinString[vl_E];
    delete violinString[vl_A];
    delete violinString[vl_D];
    delete violinString[vl_G];
}

void ViolinInstrument::reset() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        violinString[st]->reset();
    }
    for (int i = 0; i<BRIDGE_BUFFER_SIZE; i++) {
        bridge_buffer[i] = 0.0;
    }
}

void ViolinInstrument::finger(int which_string, double ratio_from_nut)
{
    violinString[which_string]->finger(ratio_from_nut);
}

void ViolinInstrument::pluck(int which_string, double ratio_from_bridge,
                             double pluck_force)
{
    violinString[which_string]->pluck(ratio_from_bridge, pluck_force);
}

void ViolinInstrument::bow(int which_string, double bow_ratio_from_bridge,
                           double bow_force, double bow_velocity)
{
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


void ViolinInstrument::body_impulse(int num_samples)
{
    for (int i=0; i<num_samples; i++) {
#ifdef NO_CONVOLUTION
        f_hole[i] = NO_CONVOLUTION_AMPLIFY*bridge_buffer[bridge_read_index];
#else
        f_hole[i] = 0.0;
        int bi=bridge_read_index;
        for (int ki=0; ki < PC_KERNEL_SIZE; ki++) {
            f_hole[i] += bridge_buffer[bi] * pc_kernel[ki];
            // update read pointer
            bi++;
            bi &= BRIDGE_BUFFER_SIZE - 1;
        }
#endif
        // update pointers
        bridge_read_index++;
        bridge_read_index &= BRIDGE_BUFFER_SIZE - 1;
    }
}

void ViolinInstrument::wait_samples(short *buffer, int num_samples)
{
    int remaining = num_samples;
    int position = 0;
    while (remaining > NORMAL_BUFFER_SIZE) {
        if (buffer == NULL) {
            handle_buffer(NULL, NORMAL_BUFFER_SIZE);
        } else {
            handle_buffer(buffer+position, NORMAL_BUFFER_SIZE);
        }
        remaining -= NORMAL_BUFFER_SIZE;
        position += NORMAL_BUFFER_SIZE;
    }
    handle_buffer(buffer+position, remaining);
}

void ViolinInstrument::handle_buffer(short output[], int num_samples)
{
    // calculate string buffers
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        violinString[st]->fill_buffer(violin_string_buffer[st], num_samples);
    }

    // calculate bridge buffer from strings
    for (int i=0; i<num_samples; i++) {
        bridge_buffer[bridge_write_index] = 0.0;
        for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
            bridge_buffer[bridge_write_index] += violin_string_buffer[st][i];
        }
        // update pointer
        bridge_write_index++;
        bridge_write_index &= BRIDGE_BUFFER_SIZE - 1;
    }

    // calculates f_hole
    body_impulse(num_samples);

    // bail if we don't want the output
    if (output == NULL) {
        return;
    }

    for (int i=0; i<num_samples; i++) {
        output[i] = SHRT_MAX*f_hole[i];
    }
}


