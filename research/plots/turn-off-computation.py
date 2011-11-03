#!/usr/bin/env python

import numpy
import pylab
import sys
filename1 = sys.argv[1]
filename2 = sys.argv[2]

sum_squared1 = numpy.genfromtxt(filename1, delimiter='\n')
sum_squared2 = numpy.genfromtxt(filename2, delimiter='\n')
#slipstates = slipstates[begin:end]
#times = [i for i in range(len(sum_squared))]
times = [i/(44100.0/1024) for i in range(len(sum_squared1))]

#pylab.plot( times, slipstates )
pylab.semilogy( times, sum_squared1)
pylab.semilogy( times, sum_squared2)
pylab.show()

out = open(filename1 + ".times.txt", 'w')
for seconds, state in zip(times, sum_squared1):
    out.write("%g\t%g\n" % (seconds, state))
out.close()

out = open(filename2 + ".times.txt", 'w')
for seconds, state in zip(times, sum_squared2):
    out.write("%g\t%g\n" % (seconds, state))
out.close()


