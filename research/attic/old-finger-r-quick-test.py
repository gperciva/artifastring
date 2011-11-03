#!/usr/bin/env python

import sys
sys.path.append('../../build/swig')
sys.path.append('../../build/.libs')
import artifastring_instrument
ARTIFASTRING_SAMPLE_RATE = artifastring_instrument.ARTIFASTRING_INSTRUMENT_SAMPLE_RATE

import scipy.io.wavfile
import midi_pos

import scipy.fftpack
import math
import numpy

import scipy
import pylab


violin = artifastring_instrument.ArtifastringInstrument()

def note(st, fp, basename, R):
    complete = numpy.empty(0, dtype=numpy.int16)
    #bp = 0.1
    #force = 0.9
    #bv = 0.5
    pp = 0.08
    pp = 0.092475
    force = 1.0

    violin.reset()

    violin.finger(st, fp, R)
    violin.pluck(st, pp, force)
    #violin.bow_accel(st, 0.1234, 0.08, 0.2, 2.0)

    #violin.set_string_logfile(st, str("%s-%i.log" % (basename, st)))
    HOPSIZE = ARTIFASTRING_SAMPLE_RATE
    ### let string settle
    #if True:
    #    buf = numpy.empty(HOPSIZE, dtype=numpy.int16)
    #    forces = numpy.empty(HOPSIZE/4, dtype=numpy.int16)
    #    violin.wait_samples_forces_python(buf, forces)
    #complete = numpy.append(complete, buf)
    #violin.bow(st, 0.1234, 0.0, 0.5)
    if True:
        buf = numpy.empty(HOPSIZE, dtype=numpy.int16)
        forces = numpy.empty(HOPSIZE/4, dtype=numpy.int16)
        violin.wait_samples_forces_python(buf, forces)
    complete = numpy.append(complete, buf)

    scipy.io.wavfile.write(basename+".wav",
        ARTIFASTRING_SAMPLE_RATE, complete)


Rs = 10**(numpy.arange(12)/2.0 )
#print Ks
#fp = 1.0 / 3.0
fp = 1.0 / 2.0
#fp = 0.109
for R in Rs:
    basename = "out/foo-%08i" % R
    #note(3, 0.109, basename, float(K))
    note(0, fp, basename, float(R))

def bin2hertz(bin_number, sample_rate, N):
    return bin_number * sample_rate / float(N)


out = open('spects-%.2f.txt' % fp, 'w')
for R in Rs:
    basename = "out/foo-%08i" % R
    #print basename
    sample_rate, data = scipy.io.wavfile.read(basename+".wav")
    data = numpy.array(data, dtype=numpy.float)/2**15

    fft = scipy.fftpack.fft(data)[:len(data)/2]
    freqs = numpy.array([ bin2hertz(i, sample_rate, len(data))
            for i in range(len(fft)) ])

    MIN_BIN = 150
    MAX_BIN = 700
    powerfft = abs(fft)**2
    for i, p in enumerate(powerfft[MIN_BIN:MAX_BIN]):
        out.write("%g %g %g\n" % (R, freqs[MIN_BIN+i], numpy.log(p)))
    out.write("\n")


    N = len(powerfft)
    maxpower = numpy.max(powerfft, axis=None)
    for i, p in enumerate(powerfft[1:-1]):
        if powerfft[i-1] < powerfft[i] > powerfft[i+1]:
            # is a peak
            if powerfft[i] > 0.0001*maxpower:
                #print freqs[i]
                pass

    flatness = numpy.exp( 1.0/N * sum(numpy.log(powerfft)) / (
        1.0/N * sum(powerfft)))
    print "%.1f\t%.3f" % (R, flatness)
    #pylab.figure()
    #pylab.plot(abs(fft))
    #pylab.title(K)
    #pylab.show()
    #exit(1)
out.close()

exit(1)


