#!/usr/bin/env python

import numpy

out = open("positions.actions", 'w')
seconds = 0.0
for x0 in numpy.linspace(0.1, 0.2, 1000):
    text = "b %g 3 %g 1.0 1.0" % (seconds, x0)
    out.write(text + "\n")
    seconds += 0.00001
out.close()

