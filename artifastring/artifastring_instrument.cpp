/*
 * Copyright 2010--2013 Graham Percival
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
#include <map>
#include <memory>
#include <mutex>
#include <samplerate.h>

#include <iostream>

#include "artifastring/artifastring_instrument.h"
#include "artifastring/artifastring_string.h"

//#define DEBUG_WITH_WHITE_NOISE
//#define NO_AUDIO_FILTERING
//#define NO_HAPTIC_FILTERING

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


#include "constants/lowpass_4.h"
#include "constants/lowpass_3.h"
#include "constants/lowpass_2.h"
#include "constants/lowpass_1.h"

#include "constants/body_violin_1.h"
#include "constants/body_viola_1.h"
#include "constants/body_cello_1.h"


#include "constants/haptic_response_1.h"
#include "constants/haptic_response_2.h"
#include "constants/haptic_response_3.h"
#include "constants/haptic_response_4.h"

ArtifastringInstrument::ArtifastringInstrument(
    InstrumentType instrument_type,
    int instrument_number,
    const int instrument_sample_rate
) {
    m_instrument_type = instrument_type;
    for (int st=0; st < NUM_VIOLIN_STRINGS; st++) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[m_instrument_type][st];
#endif
        artifastringString[st] = new ArtifastringString(m_instrument_type,
                instrument_number, st, fs_multiply, instrument_sample_rate);
    }
    /*
    m_bridge_force_amplify = BRIDGE_FORCE_AMPLIFY[(int)m_instrument_type]
                             * SHRT_MAX / CONVOLUTION_SIZE;
    m_bow_force_amplify = BOW_FORCE_AMPLIFY[(int)m_instrument_type]
                          * SHRT_MAX;
    */

    bow_string = 0;


    // FFT stuff

    // lowpass
    for (int i=0; i<NUM_VIOLIN_STRINGS; i++) {
        string_audio_lowpass_convolution[i] = NULL;
        string_force_lowpass_convolution[i] = NULL;
        string_audio_lowpass_input[i] = NULL;
        string_force_lowpass_input[i] = NULL;
    }

    body_audio_convolution = NULL;
    //body_force_convolution = NULL;

    for (int st=0; st < NUM_VIOLIN_STRINGS; st++) {
        // enable as necessary
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[m_instrument_type][st];
#endif
        //const int fs_index = fs_multiply - 1;

        {   // lowpass setup
            const float *lowpass_time_data;
            int lowpass_num_taps;
            if (fs_multiply == 1) {
                lowpass_time_data = LOWPASS_1,
                lowpass_num_taps = NUM_TAPS_LOWPASS_1;
            } else if (fs_multiply == 2) {
                lowpass_time_data = LOWPASS_2,
                lowpass_num_taps = NUM_TAPS_LOWPASS_2;
            } else if (fs_multiply == 3) {
                lowpass_time_data = LOWPASS_3,
                lowpass_num_taps = NUM_TAPS_LOWPASS_3;
            } else if (fs_multiply == 4) {
                lowpass_time_data = LOWPASS_4,
                lowpass_num_taps = NUM_TAPS_LOWPASS_4;
            }
            
            // If the requested sample rate is the default sample rate, we're done.
            // If not, the supplied convolution has to be scaled for the new sample
            // rate.
            //
            // resample_time_data takes care of that, with memoization
            resample_time_data(lowpass_time_data,
                               lowpass_num_taps,
                               instrument_sample_rate);

            string_audio_lowpass_convolution[st] = new ArtifastringConvolution(
                fs_multiply, lowpass_time_data, lowpass_num_taps);
            string_force_lowpass_convolution[st] = new ArtifastringConvolution(
                fs_multiply, lowpass_time_data, lowpass_num_taps);
                        
            string_audio_lowpass_input[st] = string_audio_lowpass_convolution[st]->get_input_buffer();
            string_force_lowpass_input[st] = string_force_lowpass_convolution[st]->get_input_buffer();

        }


#if 0
        if (audio_convolution[fs_index] == NULL) {
            const float *time_data;
            int num_taps;

            switch (m_instrument_type) {
            case Violin: {
                const int body_number = (instrument_number +
                                         (instrument_number / BODY_VIOLIN_NUMBER_1)
                                        ) % BODY_VIOLIN_NUMBER_1;

                if (fs_multiply == 1) {
                    time_data = BODY_VIOLIN_S_1[body_number],
                    num_taps = NUM_TAPS_VIOLIN_1;
                } else if (fs_multiply == 2) {
                    time_data = BODY_VIOLIN_S_2[body_number];
                    num_taps = NUM_TAPS_VIOLIN_2;
                } else if (fs_multiply == 3) {
                    time_data = BODY_VIOLIN_S_3[body_number];
                    num_taps = NUM_TAPS_VIOLIN_3;
                } else {
                    time_data = BODY_VIOLIN_S_4[body_number];
                    num_taps = NUM_TAPS_VIOLIN_4;
                }
                break;
            }
            case Viola: {
                const int body_number = (instrument_number +
                                         (instrument_number / BODY_VIOLA_NUMBER_1)
                                        ) % BODY_VIOLA_NUMBER_1;

                if (fs_multiply == 1) {
                    time_data = BODY_VIOLA_S_1[body_number],
                    num_taps = NUM_TAPS_VIOLA_1;
                } else if (fs_multiply == 2) {
                    time_data = BODY_VIOLA_S_2[body_number],
                    num_taps = NUM_TAPS_VIOLA_2;
                } else if (fs_multiply == 3) {
                    time_data = BODY_VIOLA_S_3[body_number],
                    num_taps = NUM_TAPS_VIOLA_3;
                } else if (fs_multiply == 4) {
                    time_data = BODY_VIOLA_S_4[body_number],
                    num_taps = NUM_TAPS_VIOLA_4;
                } else {
                    printf("shouldn't happen!\n");
                }
                break;
            }
            case Cello: {
                const int body_number = (instrument_number +
                                         (instrument_number / BODY_CELLO_NUMBER_1)
                                        ) % BODY_CELLO_NUMBER_1;

                if (fs_multiply == 1) {
                    time_data = BODY_CELLO_S_1[body_number];
                    num_taps = NUM_TAPS_CELLO_1;
                } else if (fs_multiply == 2) {
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
        }
#endif
    }

    {   // body
        const float *body_time_data;
        int body_num_taps;
        switch (m_instrument_type) {
        case Violin: {
            const int body_number = (instrument_number +
                                     (instrument_number / BODY_VIOLIN_NUMBER_1)
                                    ) % BODY_VIOLIN_NUMBER_1;

            body_time_data = BODY_VIOLIN_S_1[body_number];
            body_num_taps = NUM_TAPS_VIOLIN_1;
            break;
        }
        case Viola: {
            const int body_number = (instrument_number +
                                     (instrument_number / BODY_VIOLA_NUMBER_1)
                                    ) % BODY_VIOLA_NUMBER_1;

            body_time_data = BODY_VIOLA_S_1[body_number];
            body_num_taps = NUM_TAPS_VIOLA_1;
            break;
        }
        case Cello: {
            const int body_number = (instrument_number +
                                     (instrument_number / BODY_CELLO_NUMBER_1)
                                    ) % BODY_CELLO_NUMBER_1;

            body_time_data = BODY_CELLO_S_1[body_number];
            body_num_taps = NUM_TAPS_CELLO_1;
            break;
        }
        }
        
        resample_time_data(body_time_data,
                           body_num_taps,
                           instrument_sample_rate);
        
        body_audio_convolution = new ArtifastringConvolution(
            1, body_time_data, body_num_taps);
        body_audio_input = body_audio_convolution->get_input_buffer();
    }
}

ArtifastringInstrument::~ArtifastringInstrument() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        delete artifastringString[st];
        delete string_audio_lowpass_convolution[st];
        delete string_force_lowpass_convolution[st];
    }

    if (body_audio_convolution != NULL) {
        delete body_audio_convolution;
        body_audio_convolution = NULL;
        //delete haptic_convolution[i];
        //haptic_convolution[i] = NULL;
    }
}

void ArtifastringInstrument::reset() {
    for (int st = 0; st<NUM_VIOLIN_STRINGS; st++) {
        artifastringString[st]->reset();
    }
}

void ArtifastringInstrument::finger(int which_string, float ratio_from_nut,
                                    float Kf)
{
    artifastringString[which_string]->finger(ratio_from_nut, Kf);
}

void ArtifastringInstrument::pluck(int which_string, float ratio_from_bridge,
                                   float pull_distance)
{
    artifastringString[which_string]->pluck(ratio_from_bridge, pull_distance);
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
    // FIXME: maybe not necessary?  especially force?
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        string_audio_lowpass_convolution[st]->clear_input_buffer();
        string_force_lowpass_convolution[st]->clear_input_buffer();
    }

    // calculate string buffers
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        if ((st == bow_string) && (forces != NULL)) {
            artifastringString[st]->fill_buffer_forces(
                string_audio_lowpass_input[st],
                string_force_lowpass_input[st],
                num_samples);
        } else {
            //printf("no force\t%i %i\n", st, bow_string);
            artifastringString[st]->fill_buffer_forces(
                string_audio_lowpass_input[st],
                NULL,
                num_samples);
        }
    }

    // decimate string buffers
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[m_instrument_type][st];
#endif
        //const int fs_index = fs_multiply - 1;

        float prep[NORMAL_BUFFER_SIZE*fs_multiply];
        string_audio_lowpass_convolution[st]->process(prep, fs_multiply*num_samples);
        for (int i=0; i<num_samples; i++) {
            string_audio_output[st][i] = prep[fs_multiply*i];
        }

        string_force_lowpass_convolution[st]->process(prep, fs_multiply*num_samples);
        for (int i=0; i<num_samples; i++) {
            string_force_output[st][i] = prep[fs_multiply*i];
        }
    }

    // FIXME
#if 0
    for (int i=0; i<num_samples; i++) {
        std::cout<< string_audio_output[0][i] <<std::endl;
    }
#endif


    // FIXME
    if (output != NULL) {
        memset(output, 0, sizeof(short) * num_samples);

        body_audio_convolution->clear_input_buffer();
        for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
            for (int i=0; i<num_samples; i++) {
                body_audio_input[i] += string_audio_output[st][i];
            }
        }
        float prep[NORMAL_BUFFER_SIZE];
        body_audio_convolution->process(prep, num_samples);
        for (int i=0; i<num_samples; i++) {
            output[i] = prep[i];
        }
    }

#if 0
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
        for (int i=0; i<num_samples; i++) {
            output[i] += 1e2*string_audio_output[st][i];
            forces[i] += 1e2*string_force_output[st][i];
        }
    }
#endif

#if 0
    // calculate body input from strings
    for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
        if (string_audio_lowpass_input[fs_index] != NULL) {
            audio_convolution[fs_index]->clear_input_buffer();
        }
    }
    for (int st=0; st<NUM_VIOLIN_STRINGS; st++) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
        const int fs_multiply = 1;
#else
        const int fs_multiply = FS_MULTIPLICATION_FACTOR[m_instrument_type][st];
#endif
        const int fs_index = fs_multiply - 1;
        if (string_audio_lowpass_input[fs_index] != NULL) {
            for (int i=0; i<fs_multiply*num_samples; i++) {
                string_audio_lowpass_input[fs_index][i] += violin_string_buffer[st][i];
            }
        }
    }

#ifdef DEBUG_WITH_WHITE_NOISE
    // FIXME: temp white noise
    for (int fs_index=0; fs_index<NUM_MULTIPLIERS; fs_index++) {
        if (string_audio_lowpass_input[fs_index] != NULL) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
            const int fs_multiply = 1;
#else
            const int fs_multiply = fs_index + 1;
#endif
            for (int i=0; i<num_samples*fs_multiply; i++) {
                string_audio_lowpass_input[fs_index][i] = 2.0*(double(rand()) / RAND_MAX) - 1.0;
                string_force_lowpass_input[fs_index][i] = 2.0*(double(rand()) / RAND_MAX) - 1.0;
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
            if (string_audio_lowpass_input[fs_index] != NULL) {
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
            if (string_audio_lowpass_input[fs_index] != NULL) {
#ifdef HIGH_FREQUENCY_NO_DOWNSAMPLING
                const int fs_multiply = 1;
#else
                const int fs_multiply = fs_index + 1;
#endif
                for (int i=0; i<num_samples; i++) {
                    output[i] += 1e3*string_audio_lowpass_input[fs_index][fs_multiply*i];
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
            const int fs_multiply = FS_MULTIPLICATION_FACTOR[m_instrument_type][bow_string];
#endif
            const int fs_index = fs_multiply - 1;
#ifdef NO_HAPTIC_FILTERING
            // no filtering
            const float haptic_gain = 1e4;
            for (int i=0; i<num_samples/HAPTIC_DOWNSAMPLE_FACTOR; i++) {
                forces[i] = haptic_gain * string_force_lowpass_input[fs_index][HAPTIC_DOWNSAMPLE_FACTOR*i*fs_multiply];
            }
#else
            //printf("--in--- %g\n", string_force_lowpass_input[fs_index][0] );
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

                //forces[i] = 1e4*string_force_lowpass_input[fs_index][i*fs_multiply];
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
#endif
}

#ifdef RESEARCH
int ArtifastringInstrument::get_num_skips(int which_string) {
    return artifastringString[which_string]->get_num_skips();
};
#endif

float *ArtifastringInstrument::get_string_buffer(int which_string) {
    return string_audio_output[which_string];
}

void ArtifastringInstrument::get_string_buffer_int(int which_string,
        int *buffer, int num_samples,
        int *forces, int num_samples2)
{
    //printf("reading st %i, num %i\n", which_string, num_samples);
    (void) num_samples2;
    //int gain = 0.001 * std::numeric_limits<int>::max();
    for (int i=0; i<num_samples; i++) {
        buffer[i] = string_float_to_int * string_audio_output[which_string][i];
    }

    //std::cout<< "reading from st: "<<which_string<<std::endl;
    for (int i=0; i<num_samples; i++) {
        forces[i] = string_float_to_int * string_force_output[which_string][i];
        //std::cout<< forces[i] <<std::endl;
        //std::cout<< string_force_output[which_string][i] <<std::endl;
    }
}

std::mutex ArtifastringInstrument::cache_mtx;
std::map <ArtifastringInstrument::resampledTDCacheKey,
          std::unique_ptr<float[]>> ArtifastringInstrument::time_data_cache;

void ArtifastringInstrument::resample_time_data(const float*& time_data,
                                                int& num_taps,
                                                const int sample_rate)
{
    if (sample_rate != ARTIFASTRING_INSTRUMENT_SAMPLE_RATE) {
        // In case ArtifastringInstruments are instanced concurrently
        std::lock_guard<std::mutex> lock(cache_mtx);
        
        double sr_ratio(
            static_cast<double>(sample_rate) /
            static_cast<double>(ARTIFASTRING_INSTRUMENT_SAMPLE_RATE)
        );
        long num_resampled_taps(sr_ratio*num_taps);
        resampledTDCacheKey k {time_data, sample_rate};
        std::cout << "resample request at " << sample_rate << "Hz for " << time_data << std::endl;
        
        if (time_data_cache.find(k) == time_data_cache.end()) { // Time data not in cache
            std::cout << "NOT CACHED\n";
            time_data_cache[k].reset(new float[num_resampled_taps]);
            SRC_DATA resample_spec {
                time_data,                  // data in
                time_data_cache[k].get(),   // data output
                num_taps,                   // number of input frames
                num_resampled_taps,         // number of output frames
                0L,                         // place holder (input frames used)
                0L,                         // place holder (number of frames generated)
                0,                          // place holder (end of input)
                sr_ratio                    // output sample rate / input sample rate
            };
            
            if (int err = src_simple(&resample_spec, SRC_SINC_BEST_QUALITY, 1 /* channel */))
                throw new std::string(src_strerror(err));

            //float sum_in {0};
            //float sum_resamp {0};
            
            //for(int i{0}; i < num_taps; i++) sum_in += time_data[i];
            //for(int i{0}; i < num_resampled_taps; i++) sum_resamp += time_data_cache[k].get()[i];
            
            //std::cout << "Sum over input: " << sum_in << " Sum over output: " << sum_resamp << std::endl;
            
            // Renormalise filter gain when the kernel length changes
            for (int i{0}; i < num_resampled_taps; i++) {
                std::cout << i << ", " << time_data[i] << ", " << time_data_cache[k][i] << std::endl;
                time_data_cache[k][i] /= sr_ratio;
            }
            
        }

        time_data = time_data_cache[k].get();
        num_taps = num_resampled_taps;
    }
}
