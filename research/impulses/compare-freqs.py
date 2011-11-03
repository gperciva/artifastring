#!/usr/bin/env python

import numpy
import pylab
filename_a = "violin-i-freqs.txt"
filename_b = "violin-ii-freqs.txt"
#filename_b = "spectrum.txt"
#filename_c = "fftw.txt"
#filename_d = "scipy.txt"
#
a = numpy.loadtxt(filename_a).transpose()
#a[1,:] = 10*numpy.log(numpy.exp(a[1,:]/10)**2)
a[1,:] -= max(a[1,:])
b = numpy.loadtxt(filename_b).transpose()
b[1,:] -= max(b[1,:])
#c = numpy.loadtxt(filename_c).transpose()
#c[1,:] = abs(c[1,:])
#c[1,:] /= max(c[1,:])
#c[1,:] = 20*numpy.log(c[1,:])
#d = numpy.loadtxt(filename_d).transpose()
#d[1,:] = abs(d[1,:])
#d[1,:] /= max(d[1,:])
#d[1,:] = 20*numpy.log(d[1,:])


#pylab.plot(a[0], a[1], '.-', alpha=0.6, label=filename_a)
#pylab.plot(b[0], b[1], '.-', alpha=0.6, label=filename_b)
pylab.semilogx(a[0], a[1], '.-', alpha=0.6, label=filename_a)
pylab.semilogx(b[0], b[1], '.-', alpha=0.6, label=filename_b)

pylab.legend()
pylab.show()



