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
 */

#include "monowav.h"

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
FILE* prep_wav_file(const char*filename) {
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

    hdr_.chunk_size = 16;
    hdr_.format_tag = 1;
    hdr_.num_chans = (signed short)1;
    hdr_.sample_rate = 44100;
    hdr_.bytes_per_sec = hdr_.sample_rate * 2;
    hdr_.bytes_per_samp = 2;
    hdr_.bits_per_samp = 16;
    hdr_.data_length = 0;

    hdr_.data[0] = 'd';
    hdr_.data[1] = 'a';
    hdr_.data[2] = 't';
    hdr_.data[3] = 'a';

    fwrite(&hdr_, 4, 11, sfp_);
    return sfp_;
}
// --------


MonoWav::MonoWav(const char *filename, unsigned int buffer_size)
{
    size = buffer_size;
    data = new short[size];
    index = 0;
    total_samples = 0;
    outfile = prep_wav_file(filename);
}

MonoWav::~MonoWav()
{
    writeBuffer();
    // write size to file
    fseek(outfile, 40, SEEK_SET);
    size_t filesize = 2*total_samples;
    fwrite(&filesize, 4, 1, outfile);
    // clean up
    fclose(outfile);
    delete [] data;
}

void MonoWav::increase_size(unsigned int new_buffer_size)
{
    if (index > 0) {
        writeBuffer();
    }
    delete [] data;
    size = new_buffer_size;
    data = new short[size];
}

short* MonoWav::request_fill(unsigned int num_samples)
{
    if (num_samples >= size) {
        increase_size(2*num_samples);
    }
    if ((index + num_samples) >= size) {
        writeBuffer();
    }
    // yay, pointer math!
    short *start_fill = data+index;
    index += num_samples;
    return start_fill;
}

void MonoWav::writeBuffer()
{
    total_samples += index;
    fwrite(data, sizeof(short), index, outfile);
    index = 0;
}

