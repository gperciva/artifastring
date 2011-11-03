#!/usr/bin/env python

import numpy
#import pylab

slipstates = numpy.genfromtxt('bow-slipstates.txt', delimiter='\n')
begin = 21000
end = 23000
slipstates = slipstates[begin:end]
times = [i/44100.0 for i in range(begin, end)]
#times = [i/44100.0 for i in range(len(slipstates))]

#pylab.plot( times, slipstates )
#pylab.show()

out = open('bow-friction-slipstates.txt', 'w')
for seconds, state in zip(times, slipstates):
    out.write("%g\t%g\n" % (seconds, state))
out.close()


