#!/usr/bin/env python

import sys
import math
import os.path

import numpy
import scipy.fftpack
import scipy.signal
import scipy.io.wavfile
import pylab

ZEROPADDING = 1
NORMALIZED = True
NORMALIZED = False

ONLY_END = None
ONLY_END = 8192

def zero_pad_to_next_power_two(x):
    len_power_two = int(pow(2, math.ceil(math.log(len(x),2))))
    x = numpy.append(x, numpy.zeros(len_power_two - len(x)))
    return x

def bin2hertz(bin_number, sample_rate, N):
    return bin_number * sample_rate / float(N)

def get_freqs_fft(signal, sample_rate):
    signal = zero_pad_to_next_power_two(signal)
    #window = scipy.signal.get_window('boxcar', len(signal))
    window = scipy.signal.get_window('hamming', len(signal))
    #window = scipy.signal.get_window('hanning', len(signal))
    #window = scipy.signal.get_window('flattop', len(signal))
    #window = scipy.signal.get_window('blackmanharris', len(signal))
    #window = scipy.signal.gaussian(len(signal), len(signal)/8.0)
    fft = scipy.fftpack.fft(signal*window, ZEROPADDING*len(signal))
    #fft = scipy.fftpack.fft(signal, ZEROPADDING*len(signal))
    fft_abs = abs(fft[:len(fft)/2+1])
    #fft_normalized = fft_abs
    fft_normalized = fft_abs / (sum(window))
    fft_phase = numpy.angle(fft[:len(fft)/2+1])
    #fft_db = stft.amplitude2db(fft_normalized)
    #fft_db = fft_normalized
    freqs = numpy.array([ bin2hertz(i, sample_rate, len(fft))
        for i in range(len(fft_normalized)) ])
    return freqs, fft_normalized, fft_phase



filename = sys.argv[1]
orig_filename = filename

sample_rate, data_unnormalized = scipy.io.wavfile.read(filename)
#sample_rate = 48000.0
data = (numpy.array(data_unnormalized, dtype=numpy.float64)
    / float(numpy.iinfo(data_unnormalized.dtype).max))
if ONLY_END:
    data = data[-4096:]

freq, fft, phase = get_freqs_fft(data, sample_rate)
fft_db = 20*numpy.log(fft)
#fft_db = fft

if NORMALIZED:
    fft_db -= max(fft_db)

filename = "%s-freqs.txt" % (os.path.splitext(orig_filename)[0] )
numpy.savetxt( filename, numpy.vstack( (freq, fft_db)).transpose() )

if ONLY_END:
    ts = numpy.arange( len(data_unnormalized)-len(data),
        len(data_unnormalized)) / float(sample_rate)
    filename = "%s-time.txt" % (os.path.splitext(orig_filename)[0] )
    numpy.savetxt( filename, numpy.vstack( (ts, data)).transpose() )

exit(1)

pylab.figure()
#PAPER = True
PAPER = False
if PAPER:
    pylab.semilogx(freq, fft_db)
    pylab.xlim([200, 7000])
    locs = [300, 400, 600, 800, 1000, 2000, 3000, 4000, 5000, 6000]
    labels = [str(x) for x in locs]
    pylab.xticks(locs, labels)
else:
    pylab.plot(freq, fft_db)

#pylab.ylim([-270, -100])

pylab.xlabel("freq (hz)")
pylab.ylabel("magnitude (dB)")
pylab.title(filename)
pylab.xlim([50,150])

pylab.figure()
pylab.xlim([50,150])
pylab.plot(freq, phase)

#pylab.figure()
#pylab.plot(freq, phase)
#pylab.xlabel("freq (hz)")
#pylab.ylabel("phase")
#pylab.title(filename)
#
pylab.show()

