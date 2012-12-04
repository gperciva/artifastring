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

#include <iostream>

#include "fft_convolution.h"
#include "artifastring/artifastring_constants.h"

#include <string.h>

#include <pthread.h>
static pthread_mutex_t fftwf_mutex = PTHREAD_MUTEX_INITIALIZER;


extern "C" {
#include <fftw3.h>
};


// body physical constants
/*
#include "constants/body_violin.h"
#include "constants/body_viola.h"
#include "constants/body_cello.h"
#include "constants/haptic_response_1.h"
#include "constants/haptic_response_2.h"
#include "constants/haptic_response_3.h"
*/

#if 0
// for temporary printing
#include <cmath>
#endif

// necessary to end fftw cleanly
static int shared_reference_counter = 0;


ArtifastringConvolution::ArtifastringConvolution(int fs_multiply_get,
        const float *kernel, const int num_samples)
{
    fs_multiply = fs_multiply_get;

    // **MUST** be a power of two!
    int v = 512*fs_multiply + num_samples;
    // http://graphics.stanford.edu/~seander/bithacks.html#RoundUpPowerOf2
    v--;
    v |= v >> 1;
    v |= v >> 2;
    v |= v >> 4;
    v |= v >> 8;
    v |= v >> 16;
    v++;
    //printf("f: %i\tc: %i\n", fs_multiply, v);
    convolution_size = v;
    interim_m = (convolution_size / 2) + 1;

    // critical section --------------
    pthread_mutex_lock(&fftwf_mutex);

    shared_reference_counter++;

    fft_input = (float*)fftwf_malloc(sizeof(float) * convolution_size);
    fft_output = (float*)fftwf_malloc(sizeof(float) * convolution_size);
    summed_output = (float*)fftwf_malloc(sizeof(float) * convolution_size);

    data_interim = fftwf_malloc(sizeof(fftwf_complex) * interim_m);
    kernel_interim = fftwf_malloc(sizeof(fftwf_complex) * interim_m);
    memset(kernel_interim, 0, sizeof(fftwf_complex) * interim_m);

    fftwf_plan plan_f = fftwf_plan_dft_r2c_1d(
                            convolution_size,
                            fft_input,
                            (fftwf_complex*)data_interim,
                            FFTW_ESTIMATE);
    fftwf_plan plan_b = fftwf_plan_dft_c2r_1d(
                            convolution_size,
                            (fftwf_complex*) data_interim,
                            fft_output,
                            FFTW_ESTIMATE);
    plan_f_p = (fftwf_plan*) plan_f;
    plan_b_p = (fftwf_plan*) plan_b;

    pthread_mutex_unlock(&fftwf_mutex);
    // ------------- critical section end
    //
    load_kernel_from_time_data(kernel, num_samples);

    reset();
}

ArtifastringConvolution::~ArtifastringConvolution()
{
    // critical section --------------
    pthread_mutex_lock(&fftwf_mutex);

    fftwf_destroy_plan((fftwf_plan)plan_f_p);
    fftwf_destroy_plan((fftwf_plan)plan_b_p);

    fftwf_free(data_interim);
    fftwf_free(kernel_interim);

    fftwf_free(fft_input);
    fftwf_free(fft_output);
    fftwf_free(summed_output);

    shared_reference_counter--;
    if (shared_reference_counter == 0) {
#if FFTW_CLEANUP_ELSEWHERE
        // do nothing
#else
        // must be done after ALL fftw stuff is finished
        fftwf_cleanup();
#endif
    }
    pthread_mutex_unlock(&fftwf_mutex);
    // ------------- critical section end
}

void ArtifastringConvolution::reset()
{
    clear_input_buffer();
    memset(fft_output, 0, convolution_size * sizeof(float));
    memset(summed_output, 0, convolution_size * sizeof(float));
    summed_read_index = 0;
}

void ArtifastringConvolution::clear_input_buffer()
{
    memset(fft_input, 0, convolution_size * sizeof(float));
}


#if 0
void ArtifastringConvolution::set_kernel(const float complex *kernel)
{
    //memcpy(kernel_interim, kernel, sizeof(float complex) * 2049);
    memcpy(kernel_interim, kernel, sizeof(float complex) * interim_m);
    //print_kernel(kernel);
}
#endif

#if 0
void ArtifastringConvolution::print_kernel(const void* kernel)
{
    const int fs = 22050 * fs_multiply;
    printf("--- printing kernel for %i\n", fs);
    for (int i=0; i<interim_m; i++) {
        fftwf_complex result = ((fftwf_complex*)kernel)[i];
        //printf("%g\t%g\t%g\n", i*(fs/2.0)/interim_m, crealf(result),
        //    cimagf(result));
        double response = sqrt(pow(crealf(result),2) + pow(cimagf(result),2));
        response = 20*log10(response);
        if (isinf(response)) {
            printf("%g\t%g\n", ((double)i)*(fs/2)/(interim_m-1),
                   -160.0);
        } else {
            printf("%g\t%g\n", ((double)i)*(fs/2)/(interim_m-1),
                   response);
        }
    }
}
#endif

void ArtifastringConvolution::load_kernel_from_time_data(const float *kernel,
        const int num_samples)
{
    /*
        memset( &kernel_fft_input[PC_KERNEL_SIZE],
            0, sizeof(float) * (convolution_size - PC_KERNEL_SIZE));
    */

    // critical section --------------
    pthread_mutex_lock(&fftwf_mutex);

    float* kernel_fft_input = (float*)fftwf_malloc(sizeof(float) * convolution_size);
    //memcpy(kernel_fft_input, kernel, sizeof(float) * PC_KERNEL_SIZE);
    memset( kernel_fft_input, 0, sizeof(float) * convolution_size);
    // the haptic responses are already pre-sampled, I think.
    for (int i=0; i<num_samples; i++) {
        kernel_fft_input[i] = kernel[i];
    }

    fftwf_plan kernel_plan_f = fftwf_plan_dft_r2c_1d(
                                   convolution_size,
                                   kernel_fft_input,
                                   (fftwf_complex*) kernel_interim,
                                   FFTW_ESTIMATE);
    fftwf_execute(kernel_plan_f);
    fftwf_destroy_plan(kernel_plan_f);

    fftwf_free(kernel_fft_input);

    pthread_mutex_unlock(&fftwf_mutex);
    // ------------- critical section end

    /*
        if (cutoff_freq < 0) {
            cutoff_bin = CUTOFF_FREQ * interim_m / (fs_multiply*ARTIFASTRING_INSTRUMENT_SAMPLE_RATE/2);
        } else {
            cutoff_bin = cutoff_freq * interim_m / (fs_multiply*ARTIFASTRING_INSTRUMENT_SAMPLE_RATE/2);
        }
        */
    //printf("cutoff bin: %i\n", cutoff_bin);

    /*
        for (int i=cutoff_bin; i<interim_m; i++) {
            ((fftwf_complex*)kernel_interim)[i] = 0;
        }
        */
#ifdef BODY_ONLY_LOWPASS
    for (int i=0; i<cutoff_bin; i++) {
        ((fftwf_complex*)kernel_interim)[i] = BODY_ONLY_LOWPASS;
    }
#endif
    //print_kernel(kernel_interim);
}

float* ArtifastringConvolution::get_input_buffer()
{
    return fft_input;
}

void ArtifastringConvolution::process(short *output_buffer, const int num_samples)
{
    fftwf_execute((fftwf_plan)plan_f_p);

    // pointwise multiplication
    for (int i=0; i<interim_m; i++) {
        // these will be optimized out
        const float x = ((fftwf_complex*)(data_interim))[i][0];
        const float y = ((fftwf_complex*)(data_interim))[i][1];
        const float u = ((fftwf_complex*)(kernel_interim))[i][0];
        const float v = ((fftwf_complex*)(kernel_interim))[i][1];

        ((fftwf_complex*)(data_interim))[i][0] = (x*u - y*v);
        ((fftwf_complex*)(data_interim))[i][1] = (x*v + y*u);
    }
    /*
    for (int i=cutoff_bin; i<interim_m; i++) {
        ((fftwf_complex*)(data_interim))[i] = 0;
    }
    */
    //memset(data_interim[cutoff_bin], 0, sizeof(fftwf_complex)*(interim_m-cutoff_bin));
    fftwf_execute((fftwf_plan)plan_b_p);

    // get output
    int summed_write_index = summed_read_index;
    for (int i=0; i<convolution_size; i++) {
        // body_out is un-normalized, but we take care of that
        // with the gain (set in python)
        summed_output[summed_write_index] += fft_output[i];
        // update pointer
        summed_write_index++;
        summed_write_index &= convolution_size - 1;
    }


    for (int i=0; i<num_samples; i++) {
        output_buffer[i] = summed_output[summed_read_index];
        summed_output[summed_read_index] = 0;
        summed_read_index++;
        summed_read_index &= convolution_size - 1;
    }
}


