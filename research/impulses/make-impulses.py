#!/usr/bin/env python

import wave
import struct
import glob

import numpy
import scipy.io.wavfile
import scipy.signal
import scipy.fftpack
import pylab
#MAX_SHRT = 32768.0
GAIN = 10.0

PLOT = True
PLOT = False

IMPULSES = True
#IMPULSES = False

if not IMPULSES:
    GAIN = 400.0

HEADER_BEGIN = """/* This file was automatically generated */
#ifndef BODY_%(name_upper)s_H_%(mult)i
#define BODY_%(name_upper)s_H_%(mult)i

const int NUM_TAPS_%(name_upper)s_%(mult)i = %(num_taps)i;
const int BODY_%(name_upper)s_NUMBER_%(mult)i = %(num_instruments)i;
const float BODY_%(name_upper)s_S_%(mult)i[%(num_instruments)i][%(num_taps)i] = {
    {
"""
HEADER_MIDDLE = """    }, {
"""
HEADER_BOTTOM = """    }
};
#endif
"""


def read_wave(filename):
    wav = wave.open(filename, 'r')
    nframes = wav.getnframes()
    frames = wav.readframes(nframes)
    samples = struct.unpack_from("%dh" % nframes, frames)
    return samples



def write_impulses(name, mult):
    outfile = open("body_%s_%i.h" % (name, mult), 'w')

    filenames = glob.glob('short-impulses/%s-*.wav' % name)
    filenames.sort()
    # these are used in locals()
    name_upper = name.upper()
    num_instruments = len(filenames)
    base_taps = 1607
    num_taps = base_taps * mult


    outfile.write(HEADER_BEGIN % locals())
    for i, filename in enumerate(filenames):
        #if filename != "violin-i.wav":
        #    continue
        outfile.write("        /* %s */\n" % filename)
        #wav_samples = read_wave(filename)
        if IMPULSES:
            sample_rate, wav_samples = scipy.io.wavfile.read(filename)
            wav_samples = numpy.array(wav_samples,
                dtype=numpy.float64) / float(numpy.iinfo(wav_samples.dtype).max)
        else:
            sample_rate = 44100.0
            wav_samples = numpy.zeros(2048)
            wav_samples[0] = 1.0


        wav_samples = wav_samples[:base_taps]
        resampled = wav_samples

        #pylab.plot(wav_samples)
        #mult = 2
        #resampled = scipy.signal.resample(wav_samples, mult*len(wav_samples))
        #pylab.plot(resampled)
        #pylab.plot( abs(scipy.fftpack.fft(wav_samples))/
        #    len(wav_samples) )
        #pylab.show()
        #exit(1)

        #n = 253
        #cutoff_freq = 18000.0
        #low_b = scipy.signal.firwin(n, cutoff=cutoff_freq/(mult*sample_rate/2))
        #wav_samples = scipy.signal.lfilter(low_b, 1.0, resampled)

        if PLOT:
            wav_db = abs(scipy.fftpack.fft(wav_samples))/len(wav_samples)
            fft_db = abs(scipy.fftpack.fft(resampled))/len(resampled)
            pylab.plot( 20*numpy.log10(wav_db [:len(wav_db)/2] ) )
            pylab.plot( 20*numpy.log10(fft_db [:len(fft_db)/2] ) )
            pylab.show()
        #exit(1)

        #wav_samples = -(wav_samples + low_a)
        #wav_samples[n/2] = wav_samples[n/2]+1

        #pylab.plot(wav_samples)
        #pylab.show()
        #exit(1)

        #fft = scipy.fftpack.fft(wav_samples)
        #freqs_half = numpy.array([ float(x) * (mult*sample_rate) / len(fft)
        #    for x, y in enumerate(fft[:len(fft)/2+1])])


        #if PLOT:
        #    w, h = scipy.signal.freqz(low_b)
#
 #           pylab.plot(w / numpy.pi * (sample_rate/2), 20*numpy.log(numpy.abs(h)))
        #pylab.figure()
        #pylab.plot( freqs_half,
        #    20*numpy.log(numpy.abs(fft[:len(fft)/2+1]) ))

        #    pylab.show()


        print len(wav_samples)
        for sample in wav_samples:
            value = sample * GAIN / float(len(wav_samples))
            if value == 0.0:
                outfile.write("        %0.0f,\n" % float(value))
            else:
                outfile.write("        %.20gf,\n" % float(value))
        for j in range(len(wav_samples), num_taps):
            print "why here?"
            outfile.write("        %.20gf,\n" % 0.0)
        if i < len(filenames)-1:
            outfile.write(HEADER_MIDDLE)
    outfile.write(HEADER_BOTTOM)
    outfile.close()

#for name in ['violin', 'viola', 'cello']:
#    for mult in [1, 2, 3]:
#        write_impulses(name, mult)

write_impulses('violin', 1)
write_impulses('viola', 1)
write_impulses('cello', 1)




