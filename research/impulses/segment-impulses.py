#!/usr/bin/env python

import sys
import os.path
import glob

import scipy.io.wavfile
import numpy
import pylab
import scipy.fftpack

sys.path.append("../shared")

import dsp
try:
    orig_dir= sys.argv[1]
    split_dir = sys.argv[2]
except:
    print "Need wave filename to split, and directory to put them"
    sys.exit(1)

def process(filename):
    sample_rate, data = scipy.io.wavfile.read(filename)
    data = numpy.array(data, dtype=numpy.float64)
    data = scipy.signal.decimate(data, 2)
    sample_rate /= 2.0

    cutoff = 20.0 / (sample_rate/2.0)
    #print cutoff
    #pylab.plot(data)
    b, a = scipy.signal.butter(4, cutoff, btype='highpass')
    data = scipy.signal.lfilter(b, a, data)
    #pylab.plot(data)
    #pylab.show()

    data = numpy.array(data, dtype=numpy.int32)

    data_abs = abs(data)

    ind = data_abs.argmax()
    xs = numpy.arange(0, len(data))

    orientation = float(data[ind])
    for f in xrange(ind, ind-1000, -1):
        # is a zero crossing
        #print orientation, data[f]
        if orientation * data[f] <= 0:
            zero = f
            break
    #print ind, zero

    save = data [zero : zero+4096]
    xs_save = xs[zero : zero+4096]

    #print filename, ind, zero
    #pylab.plot(xs[:ind], data[:ind])
    #pylab.plot(xs_save[:500], save[:500])
    #pylab.show()

    out_filename = os.path.join(split_dir,
            os.path.basename(filename))
    scipy.io.wavfile.write(out_filename, sample_rate, save)


    fft = scipy.fftpack.fft(save / float(numpy.iinfo(save.dtype).max))
    fftabs = abs(fft[:len(fft)/2]) / len(save)
    freqs = numpy.array([
        float(i) * sample_rate / len(fft)
        for i in xrange(len(fftabs))
        ])
    fftdb = dsp.amplitude2db(fftabs)
    data = numpy.vstack( (freqs, fftdb) ).transpose()
    numpy.savetxt(out_filename[:-4] + ".freqs.txt", data)

    data = numpy.vstack( (
        numpy.arange(0, len(save))/22050.0, save / float(2**31-1) ) ).transpose()
    numpy.savetxt(out_filename[:-4] + ".time.txt", data)
    #pylab.plot(freqs, fftdb)
    #pylab.show()
    #exit(1)


filenames = glob.glob(orig_dir + "*.wav")
filenames.sort()
for filename in filenames:
    process(filename)


