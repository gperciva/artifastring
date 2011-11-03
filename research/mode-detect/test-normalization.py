#!/usr/bin/env python

import numpy
import scipy
import pylab

import stft
fs = 1024
seconds = 1

def make_sine(freq):
    num_samples = fs*seconds
    t = numpy.linspace(0, seconds, num_samples)
    w = 2 * numpy.pi * freq
    signal = numpy.sin(w*t) + numpy.sin(10*w*t)
    return signal

sig_1 = make_sine(10)
fft_normalized_1 = stft.stft_amplitude(sig_1)

sig_6 = make_sine(10)
fft_normalized_6 = 0.5*stft.stft_amplitude(sig_6)


#pylab.plot(sig)
#pylab.plot(fft_normalized_1)
pylab.plot(stft.amplitude2db(fft_normalized_1))
pylab.plot(stft.amplitude2db(fft_normalized_6))
pylab.show()


