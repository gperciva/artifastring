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
 */

#ifndef MONOWAV_H
#define MONOWAV_H
#include <stdio.h>

/// Writes a monophonic wav file.
class MonoWav {
public:
    /**
     * @brief mundane constructor.
     * @param[in] filename Filename; \c ".wav" is recommended.
     * @param[in] buffer_size Writes data to disk in 1-second
     * (44100 sample) increments.  This increases automatically if
     * necessary.
     * @param[in] sample_rate Sample rate of the \c wav file.
     * @param[in] set_is_int Use 32-bit data instead of 16-bit.
     * @warning MonoWav does not check whether it received the
     * memory it attempted to allocate; if this occurs, it will
     * probably result in an unchecked exception crash.
     */
    MonoWav(const char *filename, int buffer_size=2048, int sample_rate=44100,
            bool set_is_int=false);

    /// @brief writes data to disk before quitting
    ~MonoWav();

    /**
     * @brief returns an address which can hold the request data.
     * @param[in] num_samples Number of samples you wish to write.
     * If this value requires a larger buffer size, more memory
     * will be allocated for you.
     * @warning MonoWav does not check whether it received the
     * memory it attempted to allocate; if this occurs, it will
     * probably result in an unchecked exception crash.
     */
    short *request_fill(int num_samples);

    /**
     * @brief returns an address which can hold the request data.
     * @param[in] num_samples Number of samples you wish to write.
     * If this value requires a larger buffer size, more memory
     * will be allocated for you.
     * @warning MonoWav does not check whether it received the
     * memory it attempted to allocate; if this occurs, it will
     * probably result in an unchecked exception crash.
     */
    int *request_fill_int(int num_samples);

private:
    void writeBuffer();
    void increase_size(int new_buffer_size);

    int size;
    int index;
    bool is_int;
    short *data_s;
    int *data_i;

    int total_samples;
    FILE *outfile;
};
#endif

