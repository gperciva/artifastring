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
 *
 */

#include "violin_instrument.h"
#include "violin_constants.h"
#include <limits.h>

#ifdef THREADS
#define THREAD_STATE_READY 0
#define THREAD_STATE_START 1
#define THREAD_STATE_END 2
inline void ViolinInstrument::waitReady(int id) {
    boost::mutex::scoped_lock lock(ready_mutex[id]);
    while (!(threads_status[id] == THREAD_STATE_READY)) {
        ready_cond[id].wait(lock);
    }
}
inline void ViolinInstrument::waitStartOrEnd(int id) {
    boost::mutex::scoped_lock lock(start_mutex[id]);
    // keep on looping until you see THREAD_STATE_START
    // or THREAD_STATE_END
    while (threads_status[id] == THREAD_STATE_READY) {
        start_cond[id].wait(lock);
    }
}
inline void ViolinInstrument::sendReady(int id) {
    boost::mutex::scoped_lock lock(ready_mutex[id]);
    threads_status[id] = THREAD_STATE_READY;
    ready_cond[id].notify_one();
}
inline void ViolinInstrument::sendStart(int id) {
    boost::mutex::scoped_lock lock(start_mutex[id]);
    threads_status[id] = THREAD_STATE_START;
    start_cond[id].notify_one();
}

void ViolinInstrument::thread_tick(int id) {
    sendReady(id);
    while (true) {
        waitStartOrEnd(id);
        if (threads_status[id] == THREAD_STATE_END) {
            break;
        }

        violinString[id]->fillBuffer(violin_string_buffer[id],
                                     thread_calc_samples);

        sendReady(id);
    }
}
#endif

ViolinInstrument::ViolinInstrument(int random_seed) {
    violinString[3] = new ViolinString(vl_E, 4*random_seed+0);
    violinString[2] = new ViolinString(vl_A, 4*random_seed+1);
    violinString[1] = new ViolinString(vl_D, 4*random_seed+2);
    violinString[0] = new ViolinString(vl_G, 4*random_seed+3);

    for (unsigned int i = 0; i<BRIDGE_BUFFER_SIZE; i++) {
        bridge_buffer[i] = 0.0;
    }
    // before you doubt this, draw a ring buffer diagram
    bridge_write_index = 0;
    bridge_read_index = BRIDGE_BUFFER_SIZE-PC_KERNEL_SIZE+1;

#ifdef THREADS
    for (unsigned int id = 0; id<4; id++) {
        threads_status[id] = THREAD_STATE_START;
        threads[id] = boost::thread(&ViolinInstrument::thread_tick, this, id);
    }
    // wait for all threads to be finished.
    for (int id=0; id < 4; id++) {
        waitReady(id);
    }
#endif
}

ViolinInstrument::~ViolinInstrument() {
#ifdef THREADS
    for (unsigned int id = 0; id<4; id++) {
        {
            boost::mutex::scoped_lock lock(start_mutex[id]);
            threads_status[id] = THREAD_STATE_END;
            start_cond[id].notify_one();
        }
    }
    for (unsigned int id = 0; id<4; id++) {
        threads[id].join();
    }
#endif
    delete violinString[vl_E];
    delete violinString[vl_A];
    delete violinString[vl_D];
    delete violinString[vl_G];
}

void ViolinInstrument::reset() {
    for (unsigned int id = 0; id<4; id++) {
        violinString[id]->reset();
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


void ViolinInstrument::body_impulse(unsigned int num_samples)
{
    for (unsigned int i=0; i<num_samples; i++) {
        f_hole[i] = 0.0;
        unsigned int bi=bridge_read_index;
        for (unsigned int ki=0; ki < PC_KERNEL_SIZE; ki++) {
            f_hole[i] += bridge_buffer[bi] * pc_kernel[ki];
            // update read pointer
            bi++;
            bi &= BRIDGE_BUFFER_SIZE_MINUS_ONE;
        }
        // update pointers
        bridge_read_index++;
        bridge_read_index &= BRIDGE_BUFFER_SIZE_MINUS_ONE;
    }
}

void ViolinInstrument::wait_samples(short *buffer, unsigned int num_samples)
{
    unsigned int remaining = num_samples;
    unsigned int position = 0;
    while (remaining > NORMAL_BUFFER_SIZE) {
        handleBuffer(buffer+position, NORMAL_BUFFER_SIZE);
        remaining -= NORMAL_BUFFER_SIZE;
        position += NORMAL_BUFFER_SIZE;
    }
    handleBuffer(buffer+position, remaining);
}

void ViolinInstrument::handleBuffer(short output[], unsigned int num_samples)
{
#ifdef THREADS
    thread_calc_samples = num_samples;
    // start threads to calculate string buffers
    for (unsigned int id = 0; id<4; id++) {
        sendStart(id);
    }
    // wait for all threads to be finished.
    for (unsigned int id=0; id < 4; id++) {
        waitReady(id);
    }
#else
    // calculate string buffers
    for (int id=0; id<4; id++) {
        violinString[id]->fill_buffer(violin_string_buffer[id], num_samples);
    }
#endif

    // calculate bridge buffer from strings
    for (unsigned int i=0; i<num_samples; i++) {
        bridge_buffer[bridge_write_index] = 0.0;
        for (int id=0; id<4; id++) {
            bridge_buffer[bridge_write_index] += violin_string_buffer[id][i];
        }
        bridge_write_index++;
        bridge_write_index &= BRIDGE_BUFFER_SIZE_MINUS_ONE;
    }
    body_impulse(num_samples); // calculates f_hole

    for (unsigned int i=0; i<num_samples; i++) {
        output[i] = SHRT_MAX*f_hole[i];
    }
}


