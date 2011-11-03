#!/usr/bin/env python

import wave
import struct
import glob

PLOT = False
#PLOT = True

import numpy
numpy.seterr(all='raise')
import scipy.fftpack
import scipy.signal

MAX_SHRT = 32768.0
GAIN = (1.0 / MAX_SHRT)

HEADER_BEGIN = """/* This file was automatically generated */
#ifndef HAPTIC_RESPONSE_H_%(mult)i
#define HAPTIC_RESPONSE_H_%(mult)i

const int HAPTIC_CUTOFF_BIN_%(mult)i = %(cutoff_bin)i;
const int NUM_TAPS_%(mult)i = %(num_taps)i;
const float HAPTIC_RESPONSE_%(mult)i[%(num_taps)i] = {
"""
HEADER_BOTTOM = """};
#endif
"""

SAMPLE_RATE_MAIN = 22050.0
BINS = 2049
#NUM_TAPS = 850
NUM_TAPS = 512
#NUM_TAPS = 256
GAIN = 4.0

def freq2bin(freq, mult):
    SAMPLE_RATE = mult*SAMPLE_RATE_MAIN
    return int(round(float(freq) / (SAMPLE_RATE/2) * BINS))

def draw_lines(points, mult):
    fft_db = numpy.zeros(BINS)
    for p0, p1 in zip(points[:-1], points[1:]):
        print "***", p0, p1
        x0 = freq2bin(p0[0], mult)
        x1 = freq2bin(p1[0], mult)
        y0 = p0[1]
        y1 = p1[1]
        for i in xrange(x0, x1):
            fft_db[i] = y0 + float(i-x0)*(y1-y0) / (x1-x0)
            #print i, fft_db[i-x0]
    fft_db -= min(fft_db)
    fft_db = -1*fft_db
    return fft_db
    

def write_impulse(mult):
    SAMPLE_RATE = mult*SAMPLE_RATE_MAIN
    fs = SAMPLE_RATE
    points = [ (0, 0), (3, 25), (40, 5),
        (100, -5),
    #points = [ (0, 25), (3, 25), (40, 5), (250, -18),
        (200, -15),
        (250, -18),
        (500, -10),
        (750, 2.5),
        (1000, 15),
        (1250, 25),
        (1500, 35),
        (1750, 45),
        (2000, 55),
        #(SAMPLE_RATE/2-1, 65),
        (SAMPLE_RATE/2, 0),
        ]
    min_point = min([y for x,y in points])
    num_taps = NUM_TAPS

    freqs = numpy.array([ x / (SAMPLE_RATE/2) for x,y in points])
    #gains = numpy.array([ numpy.exp(-y+min_point) for x,y in points])
    gains = numpy.array([ numpy.exp((-y+min_point)/10.0) for x,y in points])
    gains[0] = 0
    gains[-1] = 0
    #print freqs
    #print gains

    cutoff_bin = freq2bin(points[-2][0], mult)

    #fft_db = draw_lines(points, mult)

    #actual_gains = numpy.exp((fft_db-max(fft_db))/10.0)
    #cutoff_bin = int(points[-1][0]/(SAMPLE_RATE/2) * BINS)
    #print "cutoff bin:", cutoff_bin
    #actual_gains[ 0 ] = 0
    #actual_gains[ cutoff_bin : ] = 0

    #pylab.plot(fft_db)
    #pylab.plot(actual_gains, '.-')
    #pylab.xlim([0,freq2bin(2000, mult)])
    #pylab.show()

    gains *= GAIN
    taps = scipy.signal.firwin2(NUM_TAPS, freqs, gains,
        #window="blackmanharris"
        )
    #pylab.figure()
    #pylab.plot(taps)
    #pylab.figure()

    w, h = scipy.signal.freqz(taps, worN=2048)

    gains[0] = 1e-9
    gains[-1] = 1e-9
    gains_db = 20*numpy.log(gains)
    freqs = freqs*(fs/2)
    h_db = 20*numpy.log(abs(h))
    w = w/numpy.pi * (fs/2)
    if PLOT:
        import pylab

        pylab.plot(freqs, gains_db)
        pylab.plot(w, h_db)
    ##pylab.semilogx(freqs*(fs/2), 20*numpy.log(gains))
    ##pylab.semilogx(w / numpy.pi*(fs/2), 20*numpy.log(abs(h)))
    ##pylab.xlim([freq2bin(1, mult), 1.0])
        pylab.xlim([1.0, (fs/2)])

        pylab.figure()
        pylab.plot(w / numpy.pi * (fs/2), numpy.angle(h))

        pylab.show()
    if mult == 1:
        numpy.savetxt("haptic-ideal.txt",
            numpy.vstack( (freqs, gains_db) ).transpose())
        numpy.savetxt("haptic-windowed.txt",
            numpy.vstack( (w, h_db) ).transpose())
        
    #return

    outfile = open("haptic_response_%i.h" % mult, 'w')
    outfile.write(HEADER_BEGIN % locals())
    #for gain in actual_gains[:cutoff_bin]:
    for tap in taps:
        outfile.write("    %0.15ef,\n" % (tap * 512.0 / len(taps)))

    outfile.write(HEADER_BOTTOM)
    outfile.close()

write_impulse(1)
write_impulse(2)
write_impulse(3)
write_impulse(4)


