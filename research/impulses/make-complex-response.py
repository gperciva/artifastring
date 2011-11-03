#!/usr/bin/env python

import scipy.io.wavfile
#import wave
#import struct
import glob

import numpy
import scipy.fftpack

MAX_SHRT = 32768.0
GAIN = (1.0 / MAX_SHRT) * 1e-2

HEADER_BEGIN = """/* This file was automatically generated */
#ifndef BODY_%(name_upper)s_H
#define BODY_%(name_upper)s_H

extern "C" {
#include <complex.h>
}

const int BODY_%(name_upper)s_NUMBER = %(num_taps)i;
const float complex BODY_%(name_upper)s_S[%(num_taps)i][%(interim_size)i] = {
    {
"""
HEADER_MIDDLE = """    }, {
"""
HEADER_BOTTOM = """    }
};
#endif
"""

CUTOFF_FREQUENCY = 10000


#def read_wave(filename):
#    wav = wave.open(filename, 'r')
#    nframes = wav.getnframes()
#    frames = wav.readframes(nframes)
#    samples = struct.unpack_from("%dh" % nframes, frames)
#    return samples



def write_impulses(name):
    outfile = open("body_%s.h" % name, 'w')

    filenames = glob.glob('%s-*.wav' % name)
    filenames.sort()
    # these are used in locals()
    name_upper = name.upper()
    num_taps = len(filenames)
    interim_size = 1025
    outfile.write(HEADER_BEGIN % locals())
    for i, filename in enumerate(filenames):
        print filename
        if filename != "violin-i.wav":
            continue
        outfile.write("        /* %s */\n" % filename)
        sample_rate, wav_samples = scipy.io.wavfile.read(filename)
        #wav_samples = read_wave(filename)
        cutoff_bin = float(CUTOFF_FREQUENCY) / (sample_rate/2.0) * len(wav_samples)

        wav_samples_array = numpy.array(wav_samples) * GAIN
        fft = scipy.fftpack.fft(wav_samples_array, 2*len(wav_samples_array,))
        # fftwf only keeps the positive frequencies for real FFTs
        fft = fft[:len(fft)/2+1]
        print "kernel FFT'd length:", len(fft)
        #import pylab
        #pylab.loglog(abs(fft))
        #pylab.show()
        for j, sample in enumerate(fft):
            rl = sample.real
            img = sample.imag
            if j > cutoff_bin:
                rl = 0
                img = 0
            outfile.write("        %.15g + %.15g*I,\n" % (rl, img))

        #for sample in wav_samples:
        #    value = sample / MAX_SHRT
        #    outfile.write("        %.15f,\n" % value)
        if i < len(filenames)-1:
            outfile.write(HEADER_MIDDLE)
    outfile.write(HEADER_BOTTOM)
    outfile.close()

for name in ['violin', 'viola', 'cello', '16']:
    write_impulses(name)



