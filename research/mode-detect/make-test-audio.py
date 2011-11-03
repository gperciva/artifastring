#!/usr/bin/env python

import math
import os.path

import numpy
import numpy.random
import scipy.io.wavfile
import scipy.fftpack
import scipy.optimize
import scipy.signal
import scipy.stats
import pylab

fs = 44100

def make_decay(freq, decay, seconds, relative_noise_amplitude):
    num_samples = fs*seconds
    t = numpy.linspace(0, seconds, num_samples)
    w = 2 * numpy.pi * freq
    signal = (numpy.cos(w*t) * numpy.exp(-decay*t)
        + relative_noise_amplitude * numpy.random.uniform(-1, 1, num_samples))
    signal /= max(signal)
    return signal

def other(signal):
    fft = scipy.fftpack.fft(signal)
    fft_positive = abs(fft[0:len(fft)/2])
    fft_normalized = fft_positive / float(len(signal))
    fft_power = fft_normalized**2
    
    pylab.plot(fft_power)

def write_wav(filename, data):
    data_16 = numpy.int16( data * (2**14) )
    scipy.io.wavfile.write(filename, fs, data_16)


#other(sig)
#pylab.plot(sig)
#pylab.show()

def create(freq, alpha, seconds, relative_noise):
    data = make_decay(freq, alpha, seconds, relative_noise)
    filename = "test-%if-%.1fa-%is.wav" % (
        freq, alpha, seconds)
    write_wav(filename, data)
def create_noise(freq, seconds, noise):
    num_samples = fs*seconds
    data = noise * numpy.random.uniform(-1, 1, num_samples)
    filename = "test-%if-noise.wav" % (
        freq)
    write_wav(filename, data)

noise = 1e-2
create_noise(440, 10, noise)
create(440,  10, 10, noise)
create(440,   1, 10, noise)
create(440, 0.1, 10, noise)



