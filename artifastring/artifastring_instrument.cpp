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

//#include <Eigen/Dense> // must be before including complex

#include <limits.h>
#include <cstddef>

#include <algorithm>

#include <iostream>

#include "artifastring/artifastring_instrument.h"
#include "artifastring/artifastring_string.h"

//#define DEBUG_WITH_WHITE_NOISE
//#define NO_AUDIO_FILTERING
#define NO_HAPTIC_FILTERING

#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
#define NO_AUDIO_FILTERING
#define NO_HAPTIC_FILTERING
#endif

//#include <complex>
//extern "C" {
//#include <complex.h>
//#include <fftw3.h>
//};

#include <stdio.h>


#include "constants/body_violin_4.h"
#include "constants/body_violin_3.h"
#include "constants/body_violin_2.h"
#include "constants/body_violin_1.h"
#include "constants/body_viola_4.h"
#include "constants/body_viola_2.h"
#include "constants/body_viola_1.h"
#include "constants/body_cello_2.h"
#include "constants/body_cello_1.h"


#include "constants/haptic_response_1.h"
#include "constants/haptic_response_2.h"
#include "constants/haptic_response_3.h"
#include "constants/haptic_response_4.h"

ArtifastringInstrument::ArtifastringInstrument(
    InstrumentType instrument_type_get,
    int instrument_number) {
    instrument_type = instrument_type_get;
    for (int st=0; st < NUM_VIOLIN_STRINGS; st++) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[instrument_type][st];
#endif
        // FIXME: debug impulses only!
        artifastringString[st] = new ArtifastringString(instrument_type,
                0, st, fs_multiply);
        //artifastringString[st] = new ArtifastringString(instrument_type,
        //        instrument_number, st, fs_multiply);
    }
    /*
    m_bridge_force_amplify = BRIDGE_FORCE_AMPLIFY[(int)instrument_type]
                             * SHRT_MAX / CONVOLUTION_SIZE;
    m_bow_force_amplify = BOW_FORCE_AMPLIFY[(int)instrument_type]
                          * SHRT_MAX;
    */

    bow_string = 0;


    // FFT stuff
    for (int i=0; i<NUM_MULTIPLIERS; i++) {
        // init as unused
        audio_convolution[i] = NULL;
        haptic_convolution[i] = NULL;
        string_audio_output[i] = NULL;
        string_haptic_output[i] = NULL;
    }
    for (int st=0; st < NUM_VIOLIN_STRINGS; st++) {
        // enable as necessary
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[instrument_type][st];
#endif
        const int fs_index = fs_multiply - 1;
        if (audio_convolution[fs_index] == NULL) {
            const float *time_data;
            int num_taps;

            switch (instrument_type) {
            case Violin: {
                if (fs_multiply == 1) {
                    const int body_number = ((int) instrument_number) % BODY_VIOLIN_NUMBER_1;
                    time_data = BODY_VIOLIN_S_1[body_number],
                    num_taps = NUM_TAPS_VIOLIN_1;
                } else if (fs_multiply == 2) {
                    const int body_number = ((int) instrument_number) % BODY_VIOLIN_NUMBER_2;
                    time_data = BODY_VIOLIN_S_2[body_number];
                    num_taps = NUM_TAPS_VIOLIN_2;
                } else if (fs_multiply == 3) {
                    const int body_number = ((int) instrument_number) % BODY_VIOLIN_NUMBER_3;
                    time_data = BODY_VIOLIN_S_3[body_number];
                    num_taps = NUM_TAPS_VIOLIN_3;
                } else {
                    const int body_number = ((int) instrument_number) % BODY_VIOLIN_NUMBER_4;
                    time_data = BODY_VIOLIN_S_4[body_number];
                    num_taps = NUM_TAPS_VIOLIN_4;
                }
                break;
            }
            case Viola: {
                if (fs_multiply == 1) {
                    int body_number = ((int) instrument_number) % BODY_VIOLA_NUMBER_1;
                    time_data = BODY_VIOLA_S_1[body_number],
                    num_taps = NUM_TAPS_VIOLA_1;
                } else if (fs_multiply == 2) {
                    int body_number = ((int) instrument_number) % BODY_VIOLA_NUMBER_2;
                    time_data = BODY_VIOLA_S_2[body_number],
                    num_taps = NUM_TAPS_VIOLA_2;
                } else if (fs_multiply == 4) {
                    int body_number = ((int) instrument_number) % BODY_VIOLA_NUMBER_4;
                    time_data = BODY_VIOLA_S_4[body_number],
                    num_taps = NUM_TAPS_VIOLA_4;
                } else {
                    printf("shouldn't happen!\n");
                }
                break;
            }
            case Cello: {
                if (fs_multiply == 1) {
                    int body_number = ((int) instrument_number) % BODY_CELLO_NUMBER_1;
                    time_data = BODY_CELLO_S_1[body_number];
                    num_taps = NUM_TAPS_CELLO_1;
                } else if (fs_multiply == 2) {
                    int body_number = ((int) instrument_number) % BODY_CELLO_NUMBER_2;
                    time_data = BODY_CELLO_S_2[body_number];
                    num_taps = NUM_TAPS_CELLO_2;
                } else {
                    printf("shouldn't happen!\n");
                }
                break;
            }
            }

            //printf("inst: %i\n", num_taps);
            audio_convolution[fs_index] = new ArtifastringConvolution(
                fs_multiply, time_data, num_taps);

            string_audio_output[fs_index] = audio_convolution[fs_index]->get_input_buffer();

            if (fs_multiply == 1) {
                time_data = HAPTIC_RESPONSE_1;
                num_taps = NUM_TAPS_1;
            } else if (fs_multiply == 2) {
                time_data = HAPTIC_RESPONSE_2;
                num_taps = NUM_TAPS_2;
            } else if (fs_multiply == 3) {
                time_data = HAPTIC_RESPONSE_3;
                num_taps = NUM_TAPS_3;
            } else {
                time_data = HAPTIC_RESPONSE_4;
                num_taps = NUM_TAPS_4;
            }

            //printf("haptic: %i\n", num_taps);
            haptic_convolution[fs_index] = new ArtifastringConvolution(
                fs_multiply, time_data, num_taps);
            string_haptic_output[fs_index] = haptic_convolution[fs_index]->get_input_buffer();
        }
    }

}

ArtifastringInstrument::~ArtifastringInstrument() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        delete artifastringString[st];
    }

    for (int i=0; i<NUM_MULTIPLIERS; i++) {
        if (audio_convolution[i] != NULL) {
            delete audio_convolution[i];
            audio_convolution[i] = NULL;
            delete haptic_convolution[i];
            haptic_convolution[i] = NULL;
        }
    }
}

void ArtifastringInstrument::reset() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        artifastringString[st]->reset();
    }
}

void ArtifastringInstrument::finger(int which_string, float ratio_from_nut,
                                    float finger_K)
{
    artifastringString[which_string]->finger(ratio_from_nut, finger_K);
}

void ArtifastringInstrument::pluck(int which_string, float ratio_from_bridge,
                                   float pluck_force)
{
    artifastringString[which_string]->pluck(ratio_from_bridge, pluck_force);
}

void ArtifastringInstrument::bow(int which_string, float bow_ratio_from_bridge,
                                 float bow_force, float bow_velocity)
{
    // release previous string
    // TODO: handle double stops
    if (which_string != bow_string) {
        //printf("bow new, old: %i %i\n", which_string, bow_string);
        artifastringString[bow_string]->string_release();
        bow_string = which_string;
    }
    // start new string
    artifastringString[which_string]->bow(bow_ratio_from_bridge,
                                          bow_force, bow_velocity);
}

void ArtifastringInstrument::bow_accel(int which_string, float bow_ratio_from_bridge,
                                       float bow_force, float bow_velocity_target, float bow_accel)
{
    bow_string = which_string;
    artifastringString[which_string]->bow_accel(bow_ratio_from_bridge,
            bow_force, bow_velocity_target,
            bow_accel);
}


String_Physical ArtifastringInstrument::get_physical_constants(int which_string)
{
    return artifastringString[which_string]->get_physical_constants();
}

void ArtifastringInstrument::set_physical_constants(int which_string,
        String_Physical pc_new)
{
    artifastringString[which_string]->set_physical_constants(pc_new);
}

#ifdef RESEARCH
bool ArtifastringInstrument::set_string_logfile(int which_string,
        const char *filename)
{
    return artifastringString[which_string]->set_logfile(filename);
}
#endif



int ArtifastringInstrument::wait_samples(short *buffer, int num_samples)
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
    return 0;
}

int ArtifastringInstrument::wait_samples_forces(short *buffer, short *forces,
        int num_samples)
{
    //printf("wait_sample_forces, num_samples: %i\n", num_samples);
    int remaining = num_samples;
    int position = 0;
    while (remaining > NORMAL_BUFFER_SIZE) {
        if (buffer == NULL) {
            handle_buffer(NULL, NULL, NORMAL_BUFFER_SIZE); // special case
        } else {
            handle_buffer(buffer+position,
                          forces+(position/HAPTIC_DOWNSAMPLE_FACTOR),
                          NORMAL_BUFFER_SIZE);
        }
        remaining -= NORMAL_BUFFER_SIZE;
        position += NORMAL_BUFFER_SIZE;
    }
    if (remaining > 0) {
        if (buffer == NULL) {
            handle_buffer(buffer+position,
                          NULL, remaining);
        } else {
            handle_buffer(buffer+position,
                          forces+(position/HAPTIC_DOWNSAMPLE_FACTOR), remaining);
        }
    }
    return 0;
}

int ArtifastringInstrument::wait_samples_forces_python(
    short *buffer, int num_samples,
    short *forces, int num_samples2)
{
    // used to fool python/numpy/swig into liking this function
    (void) num_samples2;
    return wait_samples_forces(buffer, forces, num_samples);
}

void ArtifastringInstrument::handle_buffer(short output[], short forces[],
        int num_samples)
{
    for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
        if (string_haptic_output[fs_index] != NULL) {
            haptic_convolution[fs_index]->clear_input_buffer();
        }
    }
    // FIXME: maybe not necessary?
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        memset(violin_string_buffer[st], 0, sizeof(float)*(NUM_MULTIPLIERS*NORMAL_BUFFER_SIZE));
    }

    // calculate string buffers
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        if ((st == bow_string) && (forces != NULL)) {
            //printf("force\t%i %i\n", st, bow_string);
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
            const int fs_multiply = 1;
#else
            const int fs_multiply = FS_MULTIPLICATION_FACTOR[instrument_type][st];
#endif
            const int fs_index = fs_multiply - 1;
            artifastringString[st]->fill_buffer_forces(
                violin_string_buffer[st],
                string_haptic_output[fs_index],
                num_samples);
        } else {
            //printf("no force\t%i %i\n", st, bow_string);
            artifastringString[st]->fill_buffer_forces(violin_string_buffer[st],
                    NULL,
                    num_samples);
        }
    }

    // calculate body input from strings
    for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
        if (string_audio_output[fs_index] != NULL) {
            audio_convolution[fs_index]->clear_input_buffer();
        }
    }
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[instrument_type][st];
#endif
        const int fs_index = fs_multiply - 1;
        if (string_audio_output[fs_index] != NULL) {
            for (int i=0; i<fs_multiply*num_samples; i++) {
                string_audio_output[fs_index][i] += violin_string_buffer[st][i];
            }
        }
    }

#ifdef DEBUG_WITH_WHITE_NOISE
    // FIXME: temp white noise
    for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
        if (string_audio_output[fs_index] != NULL) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
            const int fs_multiply = 1;
#else
            const int fs_multiply = fs_index + 1;
#endif
            for (int i=0; i<num_samples*fs_multiply; i++) {
                string_audio_output[fs_index][i] = 2.0*(double(rand()) / RAND_MAX) - 1.0;
                string_haptic_output[fs_index][i] = 2.0*(double(rand()) / RAND_MAX) - 1.0;
            }
        }
    }
#endif
    if (output != NULL) {
        for (int i=0; i<num_samples; i++) {
            output[i] = 0;
        }
#ifndef NO_AUDIO_FILTERING
        for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
            if (string_audio_output[fs_index] != NULL) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
                const int fs_multiply = 1;
#else
                const int fs_multiply = fs_index + 1;
#endif
                short prep[NORMAL_BUFFER_SIZE*fs_multiply];
                audio_convolution[fs_index]->process(prep,
                                                     fs_multiply*num_samples);
                for (int i=0; i<num_samples; i++) {
                    output[i] += prep[fs_multiply*i];
                }
            }
        }
#else
        //printf("num_samples %i\n", num_samples);
        // yes, this doesn't remove the aliasing!
        for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
            if (string_audio_output[fs_index] != NULL) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
                const int fs_multiply = 1;
#else
                const int fs_multiply = fs_index + 1;
#endif
                for (int i=0; i<num_samples; i++) {
                    output[i] += 1e3*string_audio_output[fs_index][fs_multiply*i];
                }
            }
        }
#endif
    }
    if (forces != NULL) {
        if (bow_string >= 0) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
            const int fs_multiply = 1;
#else
            const int fs_multiply = FS_MULTIPLICATION_FACTOR[instrument_type][bow_string];
#endif
            const int fs_index = fs_multiply - 1;
#ifdef NO_HAPTIC_FILTERING
            // no filtering
            const float haptic_gain = 1e4;
            for (int i=0; i<num_samples/HAPTIC_DOWNSAMPLE_FACTOR; i++) {
                forces[i] = haptic_gain * string_haptic_output[fs_index][HAPTIC_DOWNSAMPLE_FACTOR*i*fs_multiply];
            }
#else
            //printf("--in--- %g\n", string_haptic_output[fs_index][0] );
            const int haptic_samples_body = num_samples/HAPTIC_DOWNSAMPLE_FACTOR;
            const int haptic_samples_string = num_samples * fs_multiply;
            //printf("--- num_samples: %i\n", num_samples);
            //printf("haptic samples: %i %i\n", haptic_samples_body, haptic_samples_string);

            //short convoluted[NORMAL_BUFFER_SIZE * fs_multiply];
            short prep[NORMAL_BUFFER_SIZE*fs_multiply];

            haptic_convolution[fs_index]->process(prep, haptic_samples_string);
            //printf("%i\n", convoluted[0]);
            for (int i=0; i<haptic_samples_body; i++) {
                const int read_i = HAPTIC_DOWNSAMPLE_FACTOR*i*fs_multiply;
                //printf("%i\t%i\n", i, read_i);
                //printf("%i\n", prep[read_i]);
                forces[i] = prep[read_i];

                //forces[i] = 1e4*string_haptic_output[fs_index][i*fs_multiply];
            }
            //exit(1);
            //printf("--out-- %i\n", forces[0]);
#endif
        } else {
            for (int i=0; i<num_samples/HAPTIC_DOWNSAMPLE_FACTOR; i++) {
                forces[i] = 0;
            }
        }
    }
}

#ifdef RESEARCH
int ArtifastringInstrument::get_num_skips(int which_string) {
    return artifastringString[which_string]->get_num_skips();
};
int ArtifastringInstrument::get_string_buffer(int which_string,
        float *buffer, int num_samples
                                             ) {
    const int fs_multiply = FS_MULTIPLICATION_FACTOR[instrument_type][bow_string];
    const int string_samples = NORMAL_BUFFER_SIZE*fs_multiply;
    for (int i=0; i < string_samples; i++) {
        buffer[i] = 0;
    }
    for (int i=0; i<num_samples; i++) {
        buffer[i] = violin_string_buffer[which_string][i];
    }
    return string_samples;
}
#endif


