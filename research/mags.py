#!/usr/bin/env python

import sys
import math
import os.path

import numpy
import scipy.fftpack
import scipy.signal
import scipy.io.wavfile
import pylab

def get_mags(data, sample_rate):
    hopsize = 1024
    smallsize = int(len(data) / hopsize)

    seconds = numpy.arange(0, smallsize) * (hopsize/float(sample_rate))
    data = data[ : hopsize * smallsize ]
    data = data.reshape(smallsize, hopsize)
    rms = numpy.sqrt( numpy.sum(data**2, axis=1) ) / hopsize

    return seconds, rms

filename = sys.argv[1]
try:
    skip = sys.argv[2]
except:
    skip = False

sample_rate, data_unnormalized = scipy.io.wavfile.read(filename)
data = numpy.array(data_unnormalized, dtype=numpy.float64) / float(2**15)

seconds, mags = get_mags(data, sample_rate)

filename = "%s-mags.txt" % (os.path.splitext(filename)[0] )
numpy.savetxt( filename, numpy.vstack( (seconds, mags)).transpose() )

if not skip:
    pylab.figure()
    pylab.semilogy(seconds, mags)
    pylab.xlabel("time (seconds)")
    pylab.ylabel("RMS magnitude")
    pylab.title(filename)

    pylab.show()

