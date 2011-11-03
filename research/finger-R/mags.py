#!/usr/bin/env python

import glob
import sys
import math
import os.path

import numpy
import scipy.fftpack
import scipy.signal
import scipy.io.wavfile
import pylab

def get_mags(data, sample_rate):
    hopsize = 0.1 * sample_rate

    FS = sample_rate
    b, a = scipy.signal.iirdesign(wp = 40.0*2*numpy.pi/FS,
        ws = 20.0*2*numpy.pi/FS, gpass=3, gstop=24, ftype='butter')
    #data = scipy.signal.lfilter(b, a, data)

    print "fs: %i, hopsize: %i" % (sample_rate, hopsize)
    # remove first 100ms
    #data = data[0.1*FS:]

    smallsize = int(len(data) / hopsize)

    #seconds = numpy.arange(0, smallsize) * (hopsize/float(sample_rate))
    data = data[ : hopsize * smallsize ]
    data = data.reshape(smallsize, hopsize)
    rms = numpy.sqrt( numpy.sum(data**2, axis=1) / hopsize )

    #pylab.plot(rms)
    #pylab.show()
    cutoff_before = numpy.argmax(rms)
    #cutoff_before = 0

    rms = rms[ cutoff_before: ]
    rms = 20*numpy.log(rms)
    seconds = numpy.arange(0, len(rms)) * (hopsize/float(sample_rate))

    rms -= max(rms)

    return seconds, rms

def do_file(filename):
    sample_rate, data_unnormalized = scipy.io.wavfile.read(filename)
    data = numpy.array(data_unnormalized, dtype=numpy.float64) / float(2**15)
    
    seconds, mags = get_mags(data, sample_rate)
    
    filename = "%s-mags.txt" % (os.path.splitext(filename)[0] )
    numpy.savetxt( filename, numpy.vstack( (seconds, mags)).transpose() )
    return seconds, mags


dirname = sys.argv[1]
try:
    skip = sys.argv[2]
except:
    skip = False

opens_filenames = glob.glob(os.path.join(dirname, "open*.wav"))
firsts_filenames = glob.glob(os.path.join(dirname, "first*.wav"))
r_filenames = glob.glob(os.path.join(dirname, "pluck*.wav"))
r_filenames.sort()

ops = []
for filename in opens_filenames:
    s, m = do_file(filename)
    ops.append( (filename, s, m) )
fsts = []
for filename in firsts_filenames:
    s, m = do_file(filename)
    fsts.append( (filename, s, m) )
rs = []
for filename in r_filenames:
    s, m = do_file(filename)
    rs.append( (filename, s, m) )




if not skip:
    pylab.figure()
    pylab.xlabel("time (seconds)")
    pylab.ylabel("RMS magnitude")
    pylab.title(filename)

    for f,s,m in ops:
        if '1' in f:
            pylab.plot(s, m,
                color="blue", label=f)
        else:
            pylab.plot(s, m, color="blue")
    for f,s,m in fsts:
        if '1' in f:
            pylab.plot(s, m,
                color="green", label=f)
        else:
            pylab.plot(s, m, color="green")
    for f,s,m in rs:
        pylab.plot(s, m,
            #color="red", label=f)
            label=f)
    pylab.xlim([0, 8.0])
    pylab.ylim([-100, 0])
    pylab.legend(loc=1)
    pylab.show()

