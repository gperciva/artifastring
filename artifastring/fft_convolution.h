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

#ifndef FFT_CONVOLUTION_H
#define FFT_CONVOLUTION_H

/*
 * This file has certain hard-coded values suitable for the
 * convolution in Artifastring, which may not be applicable for
 * other purposes.
 */


class ArtifastringConvolution {
public:
    ArtifastringConvolution(int fs_multiply_get,
                            const float *kernel, const int num_samples);
    ~ArtifastringConvolution();
    void reset();

    float* get_input_buffer();
    void clear_input_buffer();

    //void set_kernel(const float complex *kernel);
    void load_kernel_from_time_data(const float *kernel, const int num_samples);

    void process(float *output_buffer, const int num_samples);

#if 0
    void print_kernel(const void* kernel);
#endif

private:
    float *fft_input;
    float *fft_output;
    float *summed_output;
    int summed_read_index;

    int fs_multiply;
    int convolution_size;
    int interim_m;

    // fftwf variables
    void *plan_f_p;
    void *plan_b_p;
    void *kernel_interim;
    void *data_interim;
};

#endif



