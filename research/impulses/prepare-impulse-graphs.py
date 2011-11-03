#!/usr/bin/env python

import sys
import os.path

import scipy.io.wavfile
import scipy.fftpack
import scipy.signal
import numpy
import pylab

try:
    orig_filename = sys.argv[1]
except:
    print "Need wave filename to analyze"
    exit(1)


def get_samples_ts_fft(wav_filename):
    sample_rate, data_unnormalized = scipy.io.wavfile.read(wav_filename)
    data = data_unnormalized / float(numpy.iinfo(data_unnormalized.dtype).max)
    #data = data_unnormalized / max(data_unnormalized)
    
    WINDOWSIZE = 2048
    def bin2hertz(bin_number):
        return float(bin_number) * sample_rate / WINDOWSIZE
    
    window_function = scipy.signal.get_window("blackman", WINDOWSIZE)
    fft = scipy.fftpack.fft(data*window_function)
    fft_mag = abs(fft[0:len(fft)/2]) / WINDOWSIZE
    ts = [ bin2hertz(i) for i in range(len(fft_mag))]
    return data, ts, fft_mag

data, ts, fft_mag = get_samples_ts_fft(orig_filename)
out = open(orig_filename + '-time.txt', 'w')
for i in range(len(data)):
    text = "%.8g\t%.8g\n" % ( float(i), data[i] )
    out.write(text)
out.close()



out = open(orig_filename + '-spectral.txt', 'w')
for i in range(len(fft_mag)):
    text = "%.8g\t%.8g\n" % ( ts[i], fft_mag[i] )
    out.write(text)
out.close()

exit(1)

import glob
files = glob.glob("*.wav")
files.sort()
for f in files[1:4]:
    ts, fft_mag = get_ts_fft(f)
    pylab.loglog(ts, fft_mag, '-', label=f)

pylab.legend()
pylab.show()



