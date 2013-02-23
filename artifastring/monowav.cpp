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

#include "artifastring/monowav.h"

// from marsyas WavSink.h
struct wavhdr {
    char riff[4];            // "RIFF"
    signed int file_size;    // in bytes
    char wave[4];            // "WAVE"
    char fmt[4];             // "fmt "
    signed int chunk_size;   // in bytes (16 for PCM)
    signed short format_tag; // 1=PCM, 2=ADPCM, 3=IEEE float, 6=A-Law, 7=Mu-Law
    signed short num_chans;  // 1=mono, 2=stereo
    signed int sample_rate;
    signed int bytes_per_sec;
    signed short bytes_per_samp; // 2=16-bit mono, 4=16-bit stereo
    signed short bits_per_samp;
    char data[4];            // "data"
    signed int data_length;  // in bytes
};
// --------

// from marsyas WavSink.cpp , slightly modified
FILE* prep_wav_file(const char *filename,
                    int sample_rate=44100, bool is_int=false)
{
    wavhdr hdr_;
    FILE* sfp_ = fopen(filename, "wb");

    hdr_.riff[0] = 'R';
    hdr_.riff[1] = 'I';
    hdr_.riff[2] = 'F';
    hdr_.riff[3] = 'F';

    hdr_.file_size = 44;

    hdr_.wave[0] = 'W';
    hdr_.wave[1] = 'A';
    hdr_.wave[2] = 'V';
    hdr_.wave[3] = 'E';

    hdr_.fmt[0] = 'f';
    hdr_.fmt[1] = 'm';
    hdr_.fmt[2] = 't';
    hdr_.fmt[3] = ' ';

    hdr_.format_tag = 1;
    hdr_.chunk_size = 16;
    hdr_.num_chans = (signed short)1;
    hdr_.sample_rate = sample_rate;
    hdr_.data_length = 0;
    if (is_int) {
        hdr_.bytes_per_samp = 4;
        hdr_.bytes_per_sec = hdr_.sample_rate * 4;
        hdr_.bits_per_samp = 32;
    } else {
        hdr_.bytes_per_samp = 2;
        hdr_.bytes_per_sec = hdr_.sample_rate * 2;
        hdr_.bits_per_samp = 16;
    }

    hdr_.data[0] = 'd';
    hdr_.data[1] = 'a';
    hdr_.data[2] = 't';
    hdr_.data[3] = 'a';

    fwrite(&hdr_, 4, 11, sfp_);
    return sfp_;
}
// --------


MonoWav::MonoWav(const char *filename, int buffer_size, int sample_rate,
                 bool set_is_int)
{
    is_int = set_is_int;

    size = buffer_size;

    data_s = NULL;
    data_i = NULL;
    if (is_int) {
        data_i = new int[size];
        for (int i=0; i<buffer_size; i++) {
            data_i[i] = 0;
        }
    } else {
        data_s = new short[size];
        for (int i=0; i<buffer_size; i++) {
            data_s[i] = 0;
        }
    }
    index = 0;
    total_samples = 0;
    outfile = prep_wav_file(filename, sample_rate, is_int);
}

MonoWav::~MonoWav()
{
    writeBuffer();
    // write size to file
    fseek(outfile, 40, SEEK_SET);
    if (is_int) {
        size_t filesize = 4*total_samples;
        fwrite(&filesize, 4, 1, outfile);
    } else {
        size_t filesize = 2*total_samples;
        fwrite(&filesize, 4, 1, outfile);
    }
    // clean up
    fclose(outfile);
    if (is_int) {
        delete [] data_i;
    } else {
        delete [] data_s;
    }
}

void MonoWav::increase_size(int new_buffer_size)
{
    if (index > 0) {
        writeBuffer();
    }
    if (is_int) {
        delete [] data_i;
        size = new_buffer_size;
        data_i = new int[size];
    } else {
        delete [] data_s;
        size = new_buffer_size;
        data_s = new short[size];
    }
}

short* MonoWav::request_fill(int num_samples)
{
    if (num_samples >= size) {
        increase_size(2*num_samples);
    }
    if ((index + num_samples) >= size) {
        writeBuffer();
    }
    // yay, pointer math!
    short *start_fill = data_s+index;
    index += num_samples;
    return start_fill;
}

int* MonoWav::request_fill_int(int num_samples)
{
    if (num_samples >= size) {
        increase_size(2*num_samples);
    }
    if ((index + num_samples) >= size) {
        writeBuffer();
    }
    // yay, pointer math!
    int *start_fill = data_i+index;
    index += num_samples;
    return start_fill;
}

void MonoWav::writeBuffer()
{
    total_samples += index;
    if (is_int) {
        fwrite(data_i, sizeof(int), index, outfile);
    } else {
        fwrite(data_s, sizeof(short), index, outfile);
    }
    index = 0;
}

