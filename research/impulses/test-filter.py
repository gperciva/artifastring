#!/usr/bin/python

import numpy
import scipy
import scipy.fftpack
import pylab

fs = 48000
buf_length = 8192

orig = numpy.zeros(buf_length)
f0 = 440
dt = numpy.arange(buf_length) / float(fs)
for i in range(1,50):
    f = f0*i
    orig += numpy.sin(dt * f*2*numpy.pi)
    #print f

def get_db(data):
    data_abs  = abs(data)[:len(data)/2+1]
    data_db = 20*numpy.log10(data_abs)
    return data_db
    

#fft = scipy.fftpack.fft(orig, 2*buf_length)
fft = scipy.fftpack.fft(orig)
fft_orig = numpy.array(fft)

low_pass_bin = int(8000.0/fs*len(fft)/2)

for i in range(low_pass_bin, len(fft)):
    fft[i] = 0
altered = numpy.real(scipy.fftpack.ifft(fft))
fft = scipy.fftpack.fft(altered)


pylab.figure()
pylab.title("time data")
pylab.plot(orig, alpha=0.7)
pylab.figure()
pylab.plot(altered, alpha=0.7)
#pylab.plot(orig-altered)

pylab.figure()
pylab.title("frequency")
pylab.plot(get_db(fft_orig))
pylab.plot(get_db(fft))
pylab.show()


