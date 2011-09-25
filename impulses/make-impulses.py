#!/usr/bin/env python

import wave
import struct
import glob
MAX_SHRT = 32768.0

HEADER_BEGIN = """/* This file was automatically generated */
#ifndef IMPULSE_DATA_H
#define IMPULSE_DATA_H
const int PC_KERNEL_SIZE = 2048;
const int PC_KERNEL_NUMBER = %i;
const float pc_kernels[][2048] = {
    {
"""
HEADER_MIDDLE = """    }, {
"""
HEADER_BOTTOM = """}
};
#endif
"""
OUT_FILENAME = "violin_body_impulse.h"


def read_wave(filename):
    wav = wave.open(filename, 'r')
    nframes = wav.getnframes()
    frames = wav.readframes(nframes)
    samples = struct.unpack_from("%dh" % nframes, frames)
    return samples



def write_impulses():
    outfile = open(OUT_FILENAME, 'w')

    filenames = glob.glob('*.wav')
    filenames.sort()
    outfile.write(HEADER_BEGIN % len(filenames))
    for i, filename in enumerate(filenames):
        outfile.write("        /* %s */\n" % filename)
        wav_samples = read_wave(filename)
        for sample in wav_samples:
            value = sample / MAX_SHRT
            outfile.write("        %.15f,\n" % value)
        if i < len(filenames)-1:
            outfile.write(HEADER_MIDDLE)
    outfile.write(HEADER_BOTTOM)
    outfile.close()

write_impulses()

