#!/usr/bin/env python

import scipy.signal
import numpy
import pylab

values = open("pre-harmonics.txt").read().splitlines()
fft_list = map(lambda x: float(x.split()[1]), values)
x = numpy.array( map(lambda x: float(x.split()[0]), values) )
fft = numpy.array(fft_list)

(N, Wn) = scipy.signal.buttord(wp=0.2, ws=0.3, gpass=3, gstop=4)
(b, a) = scipy.signal.butter(N, Wn, btype='low')
filt = scipy.signal.lfilter(b, a, fft)

pylab.semilogy(x, fft)
pylab.semilogy(x, filt)
pylab.show()


