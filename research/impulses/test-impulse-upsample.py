#!/usr/bin/python

import numpy
import scipy
import scipy.fftpack
import scipy.io.wavfile
import pylab

fs = 48000
buf_length = 8192

sample_rate, kernel = scipy.io.wavfile.read("violin-i.wav")

def get_db(data):
    data_abs  = abs(data)[:len(data)/2+1]
    data_db = 20*numpy.log10(data_abs)
    return data_db
    

fft = scipy.fftpack.fft(kernel)
fft_orig = numpy.array(fft)

upsampled = numpy.zeros(3*len(kernel))
for i in range(len(kernel)):
    upsampled[3*i] = kernel[i]

fft = scipy.fftpack.fft(upsampled)
for i in range(len(kernel)/2+1, len(fft)):
    fft[i] = 0.0

pylab.figure()
pylab.title("frequency")
pylab.plot(get_db(fft_orig))
pylab.plot(get_db(fft))
pylab.show()


